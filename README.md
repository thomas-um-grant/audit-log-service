# Audit Log Service

## Purpose
The purpose of this service is to accept event data sent by other systems and provide an HTTP endpoint for querying recorded event data by field values.

## Background
This service is developed as part of the Canonical interview process to assess technical skills.

## Requirements of the exersise
Build an audit log service:

The service will accept event data sent by other systems and provide an HTTP endpoint for querying recorded event data by field values.
- Examples of events recorded:
	- a new customer account was created for a given identity.
	- a customer performed an action on a resource.
	- a customer was billed a certain amount.
	- a customer account was deactivated.

The list of event types is open-ended, all events should contain a common set of fields and a set of fields specific to the event type. The code should not need to be modified for it to accept a new event type. Also note that this service is write-intensive.

Model an audit trail of events received from such services with a schema that captures the invariant data content along with the variant, event-specific content. Design and document a microservice API that can receive, store, and retrieve these events.

The service should use authentication for the event submission and querying endpoints.

The microservice must be developed in Python or Go and run as an HTTP server. Try to use features available in the language of your choice and avoid extensive usage of frameworks or generated code. Feel free to use any data storage mechanisms that you find appropriate.

## Detailed design

#### Overall Architecture:

![Audit log service diagram](doc/Audit-Log-Service_Diagram.png)

The audit log service will follow a microservices architecture, consisting of the following components:
- **REST API**: Endpoints Handling incoming requests, authentication, and message validation.
- **Message Broker**: Message queue where the incoming payloads to be saved are queued.
- **Worker**: Task saving the queued messages into the database.
- **DB**: Database where the events are stored.

**Event Schema**: Schema that captures the invariant data content along with the variant, event-specific content. The schema will allow flexibility to handle any new event type without modifying the code. Below is the schema design chosen:

```json
{ 
	"event_id": "unique event identifier", 
	"event_type": "type of the event", 
	"timestamp": "timestamp when the event occurred", 
	"user_id": "identifier of the user who triggered the event", 
	"event_details": { 
		"specific_event_field_1": " specific_event_value_1",
		"specific_event_field_2": " specific_event_value_2"
		"specific_event_field_3": " specific_event_value_3"
	}
}
```

#### Authentication
To secure the endpoints, the authentication is implemented using tokens. Each request to the service's endpoints includes an authentication token in the header. The token is generated using the user authentication system JWT. I chose JWT over OAuth because there is no need to maintain the session state.

#### Event Submission
The service exposes an endpoint to receive event data from other systems. The endpoint supports HTTP POST requests. Here are the steps for event submission:
- The request contains the event data in JSON format.
- The authentication middleware validates the user's authentication token.
- The JSON payload is parsed and validated against the event schema.
- The event is stored in the database for later retrieval.

#### Event Querying
The service provides an endpoint to query recorded event data based on field values. The endpoint supports HTTP GET requests with query parameters. Here are the steps for event querying:
- The request includes query parameters specifying the field values to search for.
- The authentication middleware validates the user's authentication token.
- The events are retrieved from the database based on the provided query parameters.
- The matching events will be returned as a response in JSON format.

#### Data Storage
For this specific service, the important requirements to take into considerations are:
- The list of event types is open-ended, which means the structure of each event may vary.
- The service is write-intensive.

The first requirement indicates that a relational database might not be optimal. Both a NoSQL database or a Distributed File System architecture could be used, although I prefer a NoSQL database because I can perform validation and querying more easily without requiring additional tools or framework. 
Hence, MongoDB is used as the NoSQL database.

#### Error Handling and Loggin **TODO**
The system needs to include robust error handling mechanisms to handle exceptions, validate input data, and ensure continuity of the service. Proper logging is implemented to track errors, debug information, and monitor the service's behavior. Ironically, we log information regarding events occuring when the API is used so we can troubleshoot system errors.

#### Scaling and Performance
To handle the write-intensive nature of the service, the following aspects are considered:
- Using asynchronous processing: The event submission endpoint is decoupled from the actual event processing and storage. Events are processed and stored asynchronously to handle high loads without blocking the HTTP server.
- Employing message queues: A message queue system (RabbitMQ) is integrated to handle event processing and decouple it from the HTTP server. This allows for better scalability and fault tolerance.
- **TODO** Optimizing the database: Appropriate indexing, sharding, or partitioning strategies are used to ensure efficient storage and retrieval of events.

#### API Documentation

##### Authentication
To use the API, the users first need to obtain a JWT token:
```console
curl -X POST -H "Content-Type: application/json" -d '{"username":"<USERNAME>", "password":"<PASSWORD>"}' http://localhost:5000/login
```
##### Event Submission
To submit a new event, the users can use this command:
```console
curl -X POST -H "Content-Type: application/json" -H "Authorization: <JWT TOKEN>" -d '{"key1":"value1", "key2":"value2"}' http://localhost:5000/events
```
##### Event Querying
To get all events from the db, the users can use this command:
```console
curl -X GET -H "Authorization: <jwt-token>" http://localhost:5000/events
```
##### Expected Request formats
**TODO**
##### Expected Response formats
**TODO**
##### Authentication Requirements
**TODO**
##### Examples of usage
**TODO**

#### Testing **TODO**
Comprehensive unit tests and integration tests ensure the correctness and reliability of the service. 
The pytest testing framework automates the testing process.
Monitoring and Metrics: 
- Monitoring and metrics collection are implemented to gain insights into the service's performance and health. Prometheus is integrated to monitor metrics such as request latency, error rates, and system resource usage.
Security Considerations: 
- When designing the service, security best practices must be considered:
	- Use secure protocols (HTTPS) for communication.
	- Implement input validation and sanitization to prevent common vulnerabilities like injection attacks.
	- Follow the principle of least privilege for authentication and authorization.
	- Regularly update and patch dependencies to address security vulnerabilities.

## Implementation plan

#### Authentication with JWT
The JWT is signed using a secret key which is saved in a config file, alongside users.
A route is created to generate a token that can be used to make API calls.
```python
import jwt

app.config['SECRET_KEY'] = config.SECRET_KEY

# USERS is fixed in the config for this exersise, it would be great to improve this in the future to better manage users.
app.config['USERS'] = config.USERS

# Login route - generates and returns a JWT
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    # Find the user in the database
    user = next((user for user in users if user['username'] == username and user['password'] == password), None)

    if user:
        # Generate a JWT
        token = jwt.encode({'user_id': user['id']}, app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('utf-8')})

    return jsonify({'message': 'Invalid username or password'}), 401
```
#### API Enpoints
The Flask framework is used for this project. The endpoints (event submissions and querying) are structured as followed:
```python
from flask import Flask

app = Flask(__name__)

@app.route("/events, methods=[POST]")
def post_event():
    # Add event to DB
	
@app.route("/events, methods=[GET]")
def get_event():
    # Get event from DB
```
#### Message Broker with RabbitMQ
**TODO**
#### Worker with Celery
**TODO**
#### Data Storage with MongoDB
To create a NoSQL DB with MongoDB, the following implementation is used:
```python
from pymongo

# Connect to the MongoDB server on port 27017
client = pymongo.MongoClient('mongodb://localhost:27017/')

# Create a database
db = client['event_db']

# Create a collection (similar to a table in relational databases)
collection = db['events']
```

The events are stored in the DB following a specific schema so certain queries can be optimized.

## Tests **TODO**
What tests will I write? How will I ensure this service/feature works? How will I know when this service/feature stops working?

## Runbook
How do I launch this service/feature? How will I monitor it? How does someone else troubleshoot it?