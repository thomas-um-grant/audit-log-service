# Libraries
import os
import pika
from celery import Celery
from pymongo import MongoClient

# Initialize a Celery instance named 'worker' and configures it to use RabbitMQ as a message broker.
celery = Celery("tasks", broker="amqp://rabbit_user:rabbit_pass@rabbit//")

# Retrieve messages from RabbitMQ queue
@celery.task
def consume_message():
    # Establish connection to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    # Declare the message queue
    channel.queue_declare(queue='audit_log_queue')
    # Start consuming messages from the queue
    channel.basic_consume(queue='audit_log_queue', on_message_callback=process_callback, auto_ack=True)
    channel.start_consuming()

def process_callback(body):
    message = eval(body.decode())
    process_message.delay(message)

# Store messages to mongodb database
@celery.task
def process_message(message):
    # Establish connection to MongoDB
    mongo_database_url = os.environ.get('MONGODB_HOST')
    client = MongoClient(mongo_database_url)
    db = client['audit_log_db']
    collection = db['events']
    # Store the message in MongoDB
    collection.insert_one(message) #TODO: validation with schema: https://www.mongodb.com/docs/manual/core/schema-validation/specify-json-schema/
    client.close()
