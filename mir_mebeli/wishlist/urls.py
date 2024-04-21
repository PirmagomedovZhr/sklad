# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('mir_mebeli.wishlist.views',
    url(r'^$', 'wishlist', name='wishlist'),
    url(r'^print/$', 'wishlist_print', name='wishlist_print'),
    url(r'^add/(?P<product_id>\d+)/$', 'add_product', name='add_to_wishlist'),
    url(r'^remove/(?P<product_id>\d+)/$', 'remove_product', name='remove_from_wishlist'),
)
