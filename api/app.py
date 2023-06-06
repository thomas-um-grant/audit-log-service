# Libraries
from flask import Flask, jsonify

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# TODO:
# We need the broker url (rabbitmq) and the db url (mongodb) from the config file

# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')

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

if __name__ == '__main__':
    app.run()