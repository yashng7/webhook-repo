#!/bin/bash

gunicorn --bind 127.0.0.1:5000 --workers 2 src.main:app &

nginx -g "daemon off;"