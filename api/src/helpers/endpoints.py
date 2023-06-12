'''
Author: Thomas Grant
Copyright: © 2023 Thomas Grant
License: MIT License
'''
# Libraries
import os, json, jsonschema, time
from helpers.parser import find_keyword
from flask import jsonify, json, request, make_response
from helpers.authentication import token_required

# Verify the server is up
def sanity(app):
    @app.route('/ping', methods=['GET'])
    def ping_pong():
        return jsonify('pong!')

# Verify the Bearer token is valid
def verify_authentication(app):
    @app.route('/auth')
    @token_required(app)
    def auth(user_id):
        return 'JWT is valid'

# Post a new event to the service
def post_event(app, celery_client):
    @app.route('/event', methods=['POST'])
    @token_required(app)
    def push_message(user_id):
        timestamp = time.time()
        try:
            data = request.get_json()

            # Get the directory path of the JSON file
            json_dir = os.path.join(app.root_path, 'schemas')
            json_file_path = os.path.join(json_dir, 'event_schema.json')
            with open(json_file_path) as file:
                json_schema = json.load(file)
            jsonschema.validate(data, json_schema)
            event = {
                "_id": f"{user_id}-{data['event_type']}-{timestamp}",
                "event_type": data['event_type'],
                "user_id": user_id,
                "timestamp": timestamp,
                "event_details": data['event_details']
            }
            message = json.dumps(event)

            # Send tasks to worker through RabbitMQ
            celery_client.send_task('tasks.store_event', args=[message])

            message = {
                'status': 200,
                'message': 'Event submitted',
            }
            resp = jsonify(message)
            resp.status_code = 200
            app.logger.info(f"POST event from user: {user_id}. Event sent to worker. Event: {message}")
            return resp

        except jsonschema.exceptions.ValidationError as e:
            error_message = e.message
            app.logger.info(f"POST event error from user: {user_id}. The data sent did not match the event schema")
            return make_response(error_message, 400)
        except jsonschema.exceptions.SchemaError as e:
            error_message = e.message
            app.logger.info(f"POST event error from user: {user_id}. The event schema used is invalid")
            return make_response(error_message, 500)
        except Exception as e: #TODO: Handle different errors
            app.logger.info(f"POST event error from user: {user_id}. error: {e}")
            return jsonify({
                "error": f"{e}"
            })

# Retrieve events from the service     
def get_event(app, mongo_client):
    @app.route('/event', methods=['GET'])
    @token_required(app)
    def get_test(user_id):
        # Extract parameters and prepare for query
        args= request.args
        # Find our events table in to MongoDB
        db = mongo_client['audit_log_db']
        collection = db['events']
        # Narrow down the results based on the parameters passed
        query = {}
        if '_id' in args.keys():
            query['_id'] = args['_id']
        if 'event_type' in args.keys():
            query['event_type'] = args['event_type']
        #TODO: Maybe we should only allow the caller to have access to their events filtering by the field?
        if 'user_id' in args.keys():
            query['user_id'] = args['user_id']
        if 'timeStart' in args.keys() or 'timeEnd' in args.keys():
            if 'timeStart' not in args.keys():
                query['timestamp'] = {"$lte": float(args['timeEnd'])}
            elif 'timeEnd' not in args.keys():
                query['timestamp'] = {"$gte": float(args['timeStart'])}
            else:
                query['timestamp'] = {"$gte": float(args['timeStart']), "$lte": float(args['timeEnd'])}
        data = collection.find(query)
        result = []

        # Keyword filtering
        if 'keyword' in args.keys():
            result = find_keyword(data, args['keyword'])
        else:
            for item in data:
                result.append(item)
        app.logger.info(f"GET event from user: {user_id}. args: {args.keys()}")
        return jsonify(result)