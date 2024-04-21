# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from mir_mebeli.vacancies.views import root, vacancy

urlpatterns = patterns('',
    url(r'^$', root, name="vacancies_root"),
    url(r'^(?P<vacancy>.+)/$', vacancy, name="vacancy_view"),
)
