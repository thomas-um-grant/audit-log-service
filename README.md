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

## Runbook

#### Pre-req
If you are on a Windows machine, it's time to download WSL so you can use a Unix-like terminal:

WSL: https://learn.microsoft.com/en-us/windows/wsl/install

You need Git to download the project and Docker to build and run it, ensure to have these installed on your machine.

I recommend Docker Desktop if you are not familiar with Docker yet, the interface is clean and make it easier to play around with the service.

Download Git: https://git-scm.com/

Download Docker: https://www.docker.com/products/docker-desktop/

#### Download the project locally
Download a copy of this project on your machine:
```console
git clone https://github.com/thomas-um-grant/audit-log-service.git
```

#### Alternative to terminal
If you are not confident with the bash commands, I would suggest using Insomnia to query against this service, it has a clean interface and is free of use: https://insomnia.rest/

#### Build and run the project
Open a terminal and make sure you are at the root of the project to start it with the docker-compose.yml file
```console
docker-compose up -d
```
-d will have it run in the background to free your terminal, although you can ommit this part if you want to see what's happening live.
This command will build all the images / containers so it may take some time the first time around based on your internet and machine.
Once started, you can now access the service.

To verify the project is running, try to run this command:
```console
curl --request GET --url "http://localhost:5000/ping"
```
If it returns "pong!", you are all set!

#### Obtain a token
To use the API, the users first need to obtain a JWT token:
```console
curl --request POST --url "http://localhost:5000/login" --header "Content-Type: application/json" -d "{\"username\":\"canonical_user\", \"password\":\"canonical_pass\"}"
```
This command will return a Bearer token if you are using the right username and password.
Try to change the credentails, or fields that you are sending to see errors handled.

To verify that your Bearer token is valid, you can use the endpoint \auth:
```console
curl --request GET --url "http://localhost:5000/auth" --header "Authorization: Bearer: <BearerToken>"
```
Replace the <'BearerToken'> parameter with the token you obtained from the previous command.
If you receive a "JWT is valid" response, then you are all set!

/!\ The token is set to expire 5 min from the time it was generated for security purpose.

An error message will be returned if the token is missing, invalid, or expired.

#### Post an event
To submit a new event, the users can use this command:
```console
curl --request POST --url "http://localhost:5000/event" --header "Authorization: Bearer: <BearerToken>" --header "Content-Type: application/json" --data "{ \"event_type\": \"account creation\", \"event_details\": {\"message\": \"Thomas created an account.\", \"Interest\": [\"Sports\", \"Cooking\", \"Movies\"], \"location\": { \"city\": \"Seattle\", \"country\": \"USA\" }}}"
```
A schema is in place to receive new events:
```json
{ 
	// A string to name the event
	"event_type": "The name of the event",
	// Any dynamic object you wish, it can a be complex object such as the example below
	"event_details": {
		"message" : "Thomas created an acount.",
		"interests" : ["sports", "cooking", "movies"],
		"location" : {
			"city": "Seattle",
			"country": "USA"
		}
	}
}
```
An error will be returned if the data object sent is invalid, otherwise, it will return a 200 submitted.

#### Retrieve events
To get all events from the db, the users can use this command:
```console
curl --request GET --url "http://localhost:5000/event" --header "Authorization: Bearer: <BearerToken>"
```
This command will return all the events stored in the db. If you would like to query only certain events, you can add parameters:
- _id : The id of an event, this will return a single event. The id is constructed as followed: <'username'>-<'event_type'>-<'timestamp'>.
- event_type : This is the event_type passed in when the event was created.
- user_id : This is the username of the event creator, so "canonical_user" for this exercise.
- timeStart : This is the time from which you want to start. The events returned will be later than this time. The time must be given in Unix Timestamp for this exercise.
- timeEnd : This is the time for which you want to end. The events returned will be earlier than this time. The time must be given in Unix Timestamp for this exercise.
- keyword : This will parse through the entire content of the event to find match, it will return all events that match with the keyword.

To produce Unix times, use this website: https://www.unixtimestamp.com/

Below is an example of a query looking for all events with the event_type "account creation" after June 8th, 2023 12PM PST, containing the word "Thomas".
```console
curl --request GET --url "http://localhost:5000/event?event_type=account%20creation&timeStart=1686250800&keyword=Thomas" --header "Authorization: Bearer: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiY2Fub25pY2FsX3VzZXIiLCJleHBpcmF0aW9uIjoiMjAyMy0wNi0xMlQwNDo0MDowNS4yNDA5MjgifQ.SgMmMg2yvvfziPK0Ie6a9m9bAk1Gzr4IGJoYb5kcjlQ"
```

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
		"detail_1": "value_1",
		"detail_2": "value_2",
		"detail_3": {
			"detail_3_1": "value_3_1"
		}
	}
}
```

#### Authentication
To secure the endpoints, the authentication is implemented using tokens. Each request to the service's endpoints includes an authentication token in the header. The token is generated using the user authentication system JWT. I chose JWT over OAuth because there is no need to maintain the session state.

The JWT is signed using a secret key which is saved in a config file, alongside users.
A route (/login) is created to generate a Bearer token that can be used to make API calls.

#### Event Submission
The service exposes an endpoint to receive event data from other systems. The endpoint (/event) supports HTTP POST requests. Here are the steps for event submission:
- The request contains the event data in JSON format.
- The authentication middleware validates the user's authentication token.
- The JSON payload is parsed and validated against the event schema.
- The event is stored in the database for later retrieval.

#### Event Querying
The service provides an endpoint to query recorded event data based on field values. The endpoint (/event) supports HTTP GET requests with query parameters. Here are the steps for event querying:
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

#### Error Handling and Loggin
The system needs to include robust error handling mechanisms to handle exceptions, validate input data, and ensure continuity of the service. Proper logging is implemented to track errors, debug information, and monitor the service's behavior. Ironically, we log information regarding events occuring when the API is used so we can troubleshoot system errors.

#### Scaling and Performance
To handle the write-intensive nature of the service, the following aspects are considered:
- Using asynchronous processing: The event submission endpoint is decoupled from the actual event processing and storage. Events are processed and stored asynchronously to handle high loads without blocking the HTTP server.
- Employing message queues: A message queue system (RabbitMQ) is integrated to handle event processing and decouple it from the HTTP server. This allows for better scalability and fault tolerance. Celery sends aynchronous tasks through the message broker (RabbitMQ), which are then processed in the worker. Since the worker is in its own container, it allows for smooth scaling as additional workers can be added without interferring with the rest of the service.

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