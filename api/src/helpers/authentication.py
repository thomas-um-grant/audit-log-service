'''
Author: Thomas Grant
Copyright: © 2023 Thomas Grant
License: MIT License
'''
# Libraries
import os, jwt, json, jsonschema
from functools import wraps
from datetime import datetime, timedelta
from jwt.exceptions import ExpiredSignatureError
from flask import jsonify, request, session, make_response

# Login endpoint
def authenticate(app):
    '''
    Authenticate a user.
    Args:
        username (string): The username.
        password (string): The passwsord.

    Returns:
        HTTP object: A Bearer Token.

    Raises:
        400: data sent does not match the format expected.
        403: invalid credentials
        500: the schema is not valid
    '''
    @app.route('/login', methods=['POST'])
    def login():
        try:
            infos = request.get_json()

            # Validates request data against json schema
            json_dir = os.path.join(app.root_path, 'schemas')
            json_file_path = os.path.join(json_dir, 'login_schema.json')
            with open(json_file_path) as file:
                json_schema = json.load(file)
            jsonschema.validate(infos, json_schema)

            # Validates username and password
            if infos['username'] == app.config['CANONICAL_USER'] and infos['password'] == app.config['CANONICAL_PASS']:
                session['logged_in'] = True
                token = jwt.encode(
                    {
                        'user':infos['username'],
                        # Set the expiration of this token to 5min
                        'expiration':(datetime.now() + timedelta(seconds=300)).isoformat()
                    },
                    app.config['SECRET_KEY'],
                    algorithm="HS256"
                )
                # Returns a Bearer Token
                return jsonify({'token': token})
            else:
                return make_response('Unauthorized: Invalid credentials', 403)
        # Handle exceptions
        except jsonschema.exceptions.ValidationError as e:
            error_message = e.message
            return make_response(error_message, 400)
        except jsonschema.exceptions.SchemaError as e:
            error_message = e.message
            return make_response(error_message, 500)

# Decorator to enforce token for certain endpoints
def token_required(app):
    '''
    Ensures a Bearer token is passed in the Header and valid.
    Args:
        request: The request object.

    Returns:
        None or an error response if failed.

    Raises:
        403: token is missing, token has expired, token is invalid
    '''
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            token = None
            # Check if the Authorization header is present and extract it
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                if auth_header.startswith('Bearer:'):
                    token = auth_header[7:].strip()

            if not token:
                return make_response('Unauthorized: Token is missing', 403)
            try:
                payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])

                # Verify expiration
                expiration_str = payload['expiration']
                expiration_dt = datetime.strptime(expiration_str, '%Y-%m-%dT%H:%M:%S.%f')
                expiration_timestamp = int(expiration_dt.timestamp())
                if expiration_timestamp < datetime.utcnow().timestamp():
                    raise ExpiredSignatureError
                
                # Pass the user ID as an argument to the endpoint function
                kwargs['user_id'] = payload['user']

            except ExpiredSignatureError:
                return make_response('Unauthorized: Token expired', 403)
            except:
                return make_response('Unauthorized: Invalid Token', 403)
            
            return func(*args, **kwargs)
        return decorated
    return decorator

