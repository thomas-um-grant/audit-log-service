#!/bin/sh
cd worker
su -m app -c "celery -A worker worker --loglevel INFO"