# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('',
    url(r'^$', 'mir_mebeli.shop.views.get_cart', name='cart'),

    url(r'^add/(?P<product_id>\d+)/$', 'mir_mebeli.shop.views.cart_add_product', name='add_to_cart'),
#    url(r'^add/(?P<product_id>\d+)/(?P<quantity>\d+)/$', 'mir_mebeli.shop.views.add_to_cart', name='add_to_cart'),

    url(r'^remove/(?P<product_id>\d+)/$', 'mir_mebeli.shop.views.cart_remove_product', name='remove_from_cart'),

    url(r'^qty/set/$', 'mir_mebeli.shop.views.cart_set_product_quantity', name='cart-qty-set-blank'), # url-заготовка для js
    url(r'^qty/set/(?P<product_id>\d+)/(?P<quantity>\d+)/$', 'mir_mebeli.shop.views.cart_set_product_quantity',
        name='cart-qty-set'),

    url(r'^qty/inc/(?P<product_id>\d+)/$', 'mir_mebeli.shop.views.cart_inc_or_dec_product_quantity',
        kwargs={'mode': 'inc'}, name='cart-qty-inc'),
    url(r'^qty/dec/(?P<product_id>\d+)/$', 'mir_mebeli.shop.views.cart_inc_or_dec_product_quantity',
        kwargs={'mode': 'dec'}, name='cart-qty-dec'),
)
