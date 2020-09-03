#!/bin/bash

python3 manage.py migrate
python3 manage.py collectstatic --no-input

gunicorn reports_generator.wsgi -w 4 -t 600 -b 0.0.0.0:8000
