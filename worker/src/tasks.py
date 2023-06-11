"""Worker for Audit Log Service

Author: Thomas Grant
Copyright: © 2023 Thomas Grant
License: MIT License

This file is the entry point for the worker.
It asynchronously adds event to the MongoDB database.

It requires the following packages to be installed within the Python environment:
- celery==5.3.0
- pymongo==4.3.3
"""
# Libraries
import os
import json
from celery import Celery
from pymongo import MongoClient
from celery.utils.log import get_task_logger

# Setup logging
logger = get_task_logger(__name__)

# Initialize a Celery instance named 'worker' and configures it to use RabbitMQ as a message broker.
celery = Celery("tasks", broker=os.environ.get('RABBITMQ_HOST'))

# Store messages to mongodb database
@celery.task()
def store_event(event):
    # Reading incoming message
    data = json.loads(event)
    logger.info(f'Read message: {data}')
    # Connect to MongoDB
    mongo_database_url = os.environ.get('MONGODB_HOST')
    client = MongoClient(mongo_database_url)
    logger.info('Connected to DB successfully')
    db = client['audit_log_db']
    collection = db['events']
    # Store the message in MongoDB
    logger.info(f'Inserting message: {data}')
    collection.insert_one(data)
    client.close()
    logger.info(f'Operation completed successsfully')