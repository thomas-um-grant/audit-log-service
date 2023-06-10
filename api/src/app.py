# Libraries
from flask import Flask, json, jsonify, request, make_response, session
from datetime import datetime, timedelta
from pymongo import MongoClient
from functools import wraps
from waitress import serve
from celery import Celery
import logging
import secrets
import jwt

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
app.config['CANONICAL_USER'] = "canonical_user"
app.config['CANONICAL_PASS'] = "canonical_pass"

worker = Celery("worker", broker="amqp://rabbit_user:rabbit_pass@rabbit:5672")

# setup logging
file_handler = logging.FileHandler('app.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# setup authentication by jwt token
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None
        app.logger.info('Checking token...')
        # Check if the Authorization header is present
        if 'Authorization' in request.headers:
            # Extract the token from the Authorization header
            auth_header = request.headers['Authorization']
            # Check if the header starts with 'Bearer'
            if auth_header.startswith('Bearer:'):
                # Extract the token by removing the 'Bearer ' prefix
                token = auth_header[7:].strip()

        app.logger.info(f'Token = {token}')
        app.logger.info(f"Secret = {app.config['SECRET_KEY']}")
        if not token:
             return make_response('Unauthorized: Token is missing', 403)
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            app.logger.info(f'JWT decoded: {payload}')

        except:
             return make_response('Unauthorized: Invalid Token', 403)
        
        return func(*args, **kwargs)
    
    return decorated

# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')

@app.route('/login', methods=['POST'])
def login():
    infos = request.get_json()
    app.logger.info(f'Infos received: {infos}')
    if infos['username'] == app.config['CANONICAL_USER'] and infos['password'] == app.config['CANONICAL_PASS']:
        session['logged_in'] = True
        token = jwt.encode(
            {
                'user':infos['username'],
                # Set the expiration of this token to 3min
                'expiration':(datetime.utcnow() + timedelta(seconds=180)).isoformat()
            },
            app.config['SECRET_KEY'],
            algorithm="HS256"
        )

        return jsonify({'token': token})
    else:
        return make_response('Unauthorized: Invalid credentials', 403)

@app.route('/auth')
@token_required
def auth():
    return 'JWT is verified!'

#TODO: use loggings in code
# app.logger.info('informing')
# app.logger.warning('warning')
# app.logger.error('screaming bloody murder!')

# # connect to RabbitMQ message broker
# def create_rabbitmq_connection():
#     credentials = pika.PlainCredentials('rabbit_user', 'rabbit_pass')
#     parameters = pika.ConnectionParameters('rabbit',5672, '/', credentials)
#     connection = pika.BlockingConnection(parameters)
#     channel = connection.channel()
#     channel.queue_declare(queue='audit_log_queue')
#     return connection, channel

# post event
# TODO: post_event endpoint will take in a POST request, do validations and place it in the RabbitMQ queue
    # TODO: Verify authentication / authorization
    # TODO: Need to create the event schema used for validations
    # TODO: Handle 400s and 500s
    # TODO: Connect to RabbitMQ to queue the message (event object)

# get event
# TODO: get_event endpoint will take in a GET request, do validations and use the query passed in to return data from MongoDB
    # TODO: Verify authentication / authorization
    # TODO: Validate the params to create the DB query
    # TODO: Connect and query MongoDB
    # TODO: Handle 400s and 500s

@app.route('/event', methods=['POST'])
@token_required
def push_message():
    app.logger.info('Received POST call')
    try: #TODO: Validation
        message = json.dumps(request.get_json())
        app.logger.info(f'Message received: {message}')

        # Send tasks to worker through RabbitMQ
        worker.send_task('tasks.store_event', args=[message])

        message = {
            'status': 200,
            'message': 'Event submitted',
        }
        resp = jsonify(message)
        resp.status_code = 200

        return resp
    except Exception as e: #TODO: Handle different errors
        return jsonify({
            "error": f"{e}"
        })

@app.route('/event', methods=['GET'])
@token_required
def get_test():
    app.logger.info(f'Connecting to db...')
    # Establish connection to MongoDB
    client = MongoClient('db', 27017, username='mongo_user', password='mongo_pass')
    db = client['audit_log_db']
    collection = db['events']
    # Store the message in MongoDB
    data = collection.find({"_id":0}) 
    app.logger.info(f'Grabbed the event')
    result = []
    for item in data:
        result.append(item)
    app.logger.info(f'Event: {result}')
    client.close()
    return jsonify(result)

@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=5000)