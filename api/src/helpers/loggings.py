'''
Author: Thomas Grant
Copyright: © 2023 Thomas Grant
License: MIT License
'''
# Libraries
import logging

# Setup a local logging system for troubleshooting
def setup_logging(app):
    file_handler = logging.FileHandler('../app.log')
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)