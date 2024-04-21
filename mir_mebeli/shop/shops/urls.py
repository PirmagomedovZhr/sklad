# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from mir_mebeli.shop.shops.views import root, shop

urlpatterns = patterns('',
    url(r'^$', root, name="shops_root"),
    url(r'^(?P<shop>.+)/$', shop, name="shop_view"),
)
