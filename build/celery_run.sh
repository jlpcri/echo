#!/bin/bash

# This script for running celery on local desktop
# required: 'sudo apt-get install rabbitmq-server'

source ~/.virtualenvs/echo/bin/activate

cd ~/Projects/echo/

~/.virtualenvs/echo/bin/celery -A echo worker -l info


