# Libraries
import os
import json
from celery import Celery
from pymongo import MongoClient
from celery.utils.log import get_task_logger

# setup logging
logger = get_task_logger(__name__)

# Initialize a Celery instance named 'worker' and configures it to use RabbitMQ as a message broker.
worker = Celery("tasks", broker="amqp://rabbit_user:rabbit_pass@rabbit:5672")

# Store messages to mongodb database
@worker.task()
def store_event(event):
    data = json.loads(event)
    logger.info(f'Read message: {data}')
    logger.info('Connecting to DB...')
    # Establish connection to MongoDB
    mongo_database_url = os.environ.get('MONGODB_HOST')
    client = MongoClient(mongo_database_url)
    logger.info('Connected to DB successfully')
    db = client['audit_log_db']
    collection = db['events']
    logger.info(f'Inserting message: {data}')
    # Store the message in MongoDB
    post = {
        "_id": 0,
        "name": "test",
        "event_details": data
    }
    collection.insert_one(post) #TODO: validation with schema: https://www.mongodb.com/docs/manual/core/schema-validation/specify-json-schema/
    client.close()
    logger.info(f'Operation completed successsfully')