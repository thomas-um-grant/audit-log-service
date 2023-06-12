'''
Author: Thomas Grant
Copyright: © 2023 Thomas Grant
License: MIT License
'''
# Libraries
import secrets
from celery import Celery
from helpers.errors import *
from helpers.endpoints import *
from pymongo import MongoClient
from helpers.loggings import setup_logging
from helpers.authentication import authenticate

# Setup the configs TODO: This should be placed somewhere more secure outside of the codebase in the future
def configs(app):
    app.config.from_object(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['CANONICAL_USER'] = os.environ.get('CANONICAL_USER')
    app.config['CANONICAL_PASS'] = os.environ.get('CANONICAL_PASS')
    app.config['RABBITMQ_HOST'] = os.environ.get('RABBITMQ_HOST')
    app.config['MONGODB_HOST'] = os.environ.get('MONGODB_HOST')

# Setup the configs
def loggings(app):
    setup_logging(app)

# Setup the authentication
def authentication(app):
    authenticate(app)

# Setup the endpoints
def endpoints(app):
    # Use Celery client to push message to the RabbitMQ broker message
    celery_client = Celery("worker", broker=app.config['RABBITMQ_HOST'])
    # Use MongoDB client to get message from MongoDB database
    mongo_client = MongoClient(app.config['MONGODB_HOST'])
    # Sanity endpoint
    sanity(app)
    # Verify authentication
    verify_authentication(app)
    # POST event
    post_event(app, celery_client)
    # GET event
    get_event(app, mongo_client)
    # Closing MongoDB connection
    # mongo_client.close() #TODO: Find a clean way to close this on app close, no need to open / close for every call

# Setup the errors
def errors(app):
    handle_not_found(app)