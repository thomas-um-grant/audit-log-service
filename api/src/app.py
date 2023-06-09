# Libraries
from waitress import serve
from flask import Flask, jsonify, request
from pymongo import MongoClient
import pika
import logging

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# setup logging
# file_handler = logging.FileHandler('app.log')
# app.logger.addHandler(file_handler)
# app.logger.setLevel(logging.INFO)

# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')

#TODO: use loggings in code
# app.logger.info('informing')
# app.logger.warning('warning')
# app.logger.error('screaming bloody murder!')

# connect to RabbitMQ message broker
def create_rabbitmq_connection():
    credentials = pika.PlainCredentials('rabbit_user', 'rabbit_pass')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbit',port=5672, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue='audit_log_queue')
    return connection, channel

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
def push_message():
    try: #TODO: Validation
        data = request.get_json()
        # connection, channel = create_rabbitmq_connection()
        # channel.basic_publish(exchange='', routing_key='audit_log_queue', body=data)
        # connection.close()
        return f"Event submitted: {jsonify(data)}"
    except: #TODO: Handle different errors
        return not_found()

@app.route('/event', methods=['GET'])
def get_test():
    # Establish connection to MongoDB
    client = MongoClient('db', 27017, username='mongo_user', password='mongo_pass')
    db = client['audit_log_db']
    collection = db['events']
    # Store the message in MongoDB
    collection.find_one() 
    client.close()

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