from celery import Celery
import pika
from pymongo import MongoClient

celery = Celery('worker', broker='amqp://guest:guest@localhost:5672//')

@celery.task
def process_message(message):
    # Establish connection to MongoDB
    client = MongoClient('localhost', 27017) #TODO: Abstract these variables into config file
    db = client['audit_log_db']
    collection = db['events']
    # Store the message in MongoDB
    collection.insert_one(message)
    client.close()

# Consume messages from RabbitMQ queue
@celery.task
def consume_message():
    # Establish connection to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    # Declare the message queue
    channel.queue_declare(queue='message_queue')
    # Start consuming messages from the queue
    channel.basic_consume(queue='message_queue', on_message_callback=process_callback, auto_ack=True)
    channel.start_consuming()

def process_callback(ch, method, properties, body):
    message = eval(body.decode())
    process_message.delay(message)

if __name__ == '__main__':
    celery.worker_main(['worker', '-l', 'info'])
