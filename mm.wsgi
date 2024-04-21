import os, sys
sys.path.append('/var/www/new_sklad51')
os.environ['DJANGO_SETTINGS_MODULE'] = 'mir_mebeli.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
