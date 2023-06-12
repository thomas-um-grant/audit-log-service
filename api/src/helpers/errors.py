'''
Author: Thomas Grant
Copyright: © 2023 Thomas Grant
License: MIT License
'''
# Libraries
from flask import jsonify, request

# Handle 404 errors thrown
def handle_not_found(app):
    @app.errorhandler(404)
    def not_found(error=None):
        message = {
                'status': 404,
                'message': 'Not Found: ' + request.url,
        }
        resp = jsonify(message)
        resp.status_code = 404

        return resp

# TODO: Handle 5XX errors thrown