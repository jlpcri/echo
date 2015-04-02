#!/bin/sh

virtualenv --no-site-packages --clear env
. /usr/local/virtualenvs/echo/bin/activate

pip install --download-cache /tmp/jenkins/pip-cache -r requirements/jenkins.txt

python manage.py test --jenkins --settings=echo.settings.jenkins
