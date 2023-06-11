"""Audit Log Service

Author: Thomas Grant
Copyright: © 2023 Thomas Grant
License: MIT License

This file is the entry point for the audit log API.
It allows the user to post and get events.

It requires the following packages to be installed within the Python environment:
- Flask==2.3.2
- jsonschema==4.17.3
- pymongo==4.3.3
- celery==5.3.0
- waitress==2.1.2
- PyJWT==2.7.0

The API endpoints are:
- GET /ping -> Returns "pong!" to check the server's sanity

- POST /login -> Receive user credentials and returns a Bearer Token to access protected endpoints
- GET /auth -> Returns whether the Bearer Token is valid or not

- POST /event -> Receive event to store in the database
- GET /stats -> Returns an event from the database
"""

# Libraries
import os, sys
from flask import Flask
from helpers import setup
from waitress import serve

# Add this directory to sys.path so we can get files from everywhere
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# instantiate the app
app = Flask(__name__)

# setup app configs, logging, authentication, endpoints
setup.configs(app)
setup.loggings(app)
setup.authentication(app)
setup.endpoints(app)
setup.errors(app)

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=5000)