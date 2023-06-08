FROM python:3
# keep everything in a new folder: 'app'
WORKDIR /app
# install python dependencies
COPY ./requirements.txt /app
RUN pip install -r requirements.txt
# Copy the app files to the container
COPY ./src /app
# start the service
CMD python app.py