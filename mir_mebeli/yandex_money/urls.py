# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from .views import notice_form, check_order


urlpatterns = patterns('',
    url(r'^check$', check_order, name='yandex_money_check'),
    url(r'^aviso$', notice_form, name='yandex_money_notice'),
)
