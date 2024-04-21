# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('',
    url(r'^$', 'mir_mebeli.partners.views.index', name='partners-index'),
    url(r'^thanks/', 'mir_mebeli.partners.views.thanks', name='partners-thanks'),
)
