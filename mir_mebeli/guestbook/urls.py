# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
urlpatterns = patterns('',
    url(r'^$', 'mir_mebeli.guestbook.views.add', name='guestbook-index'),
    url(r'^send/', 'mir_mebeli.guestbook.views.add', name='guestbook-add'),
)
