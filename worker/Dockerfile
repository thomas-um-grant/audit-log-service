FROM python:3
# keep everything in a new folder: 'worker'
WORKDIR /worker
# install python dependencies
COPY ./requirements.txt /worker
RUN pip install -r requirements.txt
# Copy the app files to the container
COPY ./src /worker
# start the service
CMD celery -A tasks worker --loglevel=info