#!/bin/bash

# activate virtualenv and execute passed in command line

COMMAND=$@

SITE_DIR="/opt/app"
PROJ_DIR="/mir_mebeli"


cd ${SITE_DIR}${PROJ_DIR}

python manage.py ${COMMAND}
