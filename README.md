$$\begin{readme}$$
$$\begin{flushleft}$$
# Audit Log Service

## $${\color{green}Purpose}$$
The purpose of this service is to accept event data sent by other systems and provide an HTTP endpoint for querying recorded event data by field values.

## <code style="color : green">Background</code>
This service is developed as part of the Canonical interview process to assess technical skills.

## <font style="color:green"> Requirements of the exersise </font>
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

## <font style="color:green"> Detailed design </font>

#### <font style="color:blue"> Overall Architecture: </font>
The audit log service will follow a microservices architecture, consisting of the following components:
- **HTTP Server**: Handles incoming requests and routes them to the appropriate endpoints.
- **Event Handler**: Responsible for receiving, processing, and storing event data.
- **Data Storage**: Stores the recorded events for later retrieval.
- **Authentication Middleware**: Validates the user's authentication credentials before processing requests.
- **Event Schema**: Schema that captures the invariant data content along with the variant, event-specific content. The schema will allow flexibility to handle any new event type without modifying the code. Below is the schema design chosen:

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

#### <font style="color:blue"> Authentication </font>
To secure the endpoints, we'll implement authentication using tokens. Each request to the service's endpoints should include an authentication token in the header. The token can be generated using the user authentication system JWT. I chose JWT over OAuth because we don't need to maintain the session state.

#### <font style="color:blue"> Event Submission </font>
The service will expose an endpoint to receive event data from other systems. The endpoint will support HTTP POST requests. Here are the steps for event submission:
- The request will contain the event data in JSON format.
- The authentication middleware will validate the user's authentication token.
- The event handler will parse the JSON payload and validate the event against the event schema.
- The event will be stored in the database for later retrieval.

#### <font style="color:blue"> Event Querying </font>
The service will provide an endpoint to query recorded event data based on field values. The endpoint will support HTTP GET requests with query parameters. Here are the steps for event querying:
- The request will include query parameters specifying the field values to search for.
- The authentication middleware will validate the user's authentication token.
- The event handler will retrieve events from the database based on the provided query parameters.
- The matching events will be returned as a response in JSON format.

#### <font style="color:blue"> Data Storage </font>
For this specific service, the important requirements to take into considerations are:
- The list of event types is open-ended, which means the structure of each event may vary.
- The service is write-intensive.

The first requirement indicates that a relational database might not be optimal. Both a NoSQL database or a Distributed File System architecture could be used, although I prefer a NoSQL database because I can perform validation and querying more easily without requiring additional tools or framework. 
Hence, MongoDB will be used as the NoSQL database.

#### <font style="color:blue"> Error Handling and Loggin </font>
The system needs to include robust error handling mechanisms to handle exceptions, validate input data, and ensure continuity of the service. Proper logging will be implemented to track errors, debug information, and monitor the service's behavior. Ironically, we will log information regarding events occuring when the API is used so we can troubleshoot system errors.

#### <font style="color:blue"> Scaling and Performance </font>
To handle the write-intensive nature of the service, the following aspects are considered:
- Using asynchronous processing: The event submission endpoint is decoupled from the actual event processing and storage. Events are processed and stored asynchronously to handle high loads without blocking the HTTP server.
- Employing message queues: A message queue system (RabbitMQ) is integrated to handle event processing and decouple it from the HTTP server. This allows for better scalability and fault tolerance.
- Optimizing the database: Appropriate indexing, sharding, or partitioning strategies are used to ensure efficient storage and retrieval of events.

#### <font style="color:blue"> API Documentation </font>

##### <font style="color:orange"> Authentication </font>
To use the API, the users first need to obtain a JWT token:
```code
curl -X POST -H "Content-Type: application/json" -d '{"username":"<USERNAME>", "password":"<PASSWORD>"}' http://localhost:5000/login
```
##### <font style="color:orange"> Event Submission </font>
To submit a new event, the users can use this command:
```code
curl -X POST -H "Content-Type: application/json" -H "Authorization: <JWT TOKEN>" -d '{"key1":"value1", "key2":"value2"}' http://localhost:5000/events
```

##### <font style="color:orange"> Event Querying </font>
To get all events from the db, the users can use this command:
```code
curl -X GET -H "Authorization: <jwt-token>" http://localhost:5000/events
```

##### <font style="color:orange"> Expected Request formats </font>
// TODO
##### <font style="color:orange"> Expected Response formats </font>
// TODO
##### <font style="color:orange"> Authentication Requirements </font>
// TODO
##### <font style="color:orange"> Examples of usage </font>
// TODO

#### <font style="color:blue"> Testing </font>
Comprehensive unit tests and integration tests will ensure the correctness and reliability of the service. 
The pytest testing framework will automate the testing process.
Monitoring and Metrics: 
- Monitoring and metrics collection will be implemented to gain insights into the service's performance and health. We will integrate Prometheus to monitor metrics such as request latency, error rates, and system resource usage.
Security Considerations: 
- When designing the service, security best practices must be considered:
	- Use secure protocols (HTTPS) for communication.
	- Implement input validation and sanitization to prevent common vulnerabilities like injection attacks.
	- Follow the principle of least privilege for authentication and authorization.
	- Regularly update and patch dependencies to address security vulnerabilities.

## <font style="color:green"> Implementation plan </font>

#### <font style="color:blue"> Authentication with JWT </font>
The JWT is signed using a secret key which is saved in a config file, alongside users.
A route will be created to generate a token that can be used to make API calls.
```code
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

#### <font style="color:blue"> Data Storage with MongoDB </font>
To create a NoSQL DB with MongoDB, the following implementation is used:
```code
from pymongo

# Connect to the MongoDB server on port 27017
client = pymongo.MongoClient('mongodb://localhost:27017/')

# Create a database
db = client['event_db']

# Create a collection (similar to a table in relational databases)
collection = db['events']
```

The events will be stored in the DB following a specific schema so we can optimize certain queries

#### <font style="color:blue"> API Enpoints </font>
The Flask framework will be used for this project. The endpoints (event submissions and querying) will be structured as followed:
```code
from flask import Flask

app = Flask(__name__)

@app.route("/events, methods=[POST]")
def post_event():
    # Add event to DB
	
@app.route("/events, methods=[GET]")
def get_event():
    # Get event from DB
```

## <font style="color:green"> Tests </font>
What tests will you write? How will you ensure this service/feature works? How will you know when this service/feature stops working?
// TODO

## <font style="color:green"> Runbook </font>
How do you launch this service/feature? How will you monitor it? How does someone else troubleshoot it?
// TODO

Deployment Considerations: Choose a suitable deployment strategy based on your infrastructure and requirements:
Containerization: Use Docker to package the microservice along with its dependencies, making it easier to deploy and manage across different environments.
Orchestration: Utilize container orchestration platforms like Kubernetes to manage the deployment, scaling, and monitoring of the service.
Load balancing: If the service experiences high traffic, consider using a load balancer to distribute requests across multiple instances of the service for improved performance and availability.

$$\begin{flushleft}$$
$$\end{readme}$$