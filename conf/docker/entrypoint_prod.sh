#!/usr/bin/env bash

set -e
set -u

export ENV=prod

# Apply database migrations
echo "Apply database migrations"
#python  manage.py syncdb --noinput
#python  manage.py migrate --noinput

supervisord -c /opt/app/conf/supervisor.conf

