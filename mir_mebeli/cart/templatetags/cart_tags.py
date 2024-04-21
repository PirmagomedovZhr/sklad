# -*- coding: utf-8 -*-
from django import template


register = template.Library()


@register.inclusion_tag('cart/add_to_cart_link.html')
def add_to_cart_link(good, cart, in_text='', add_text=''):
    cart_item = cart.cached_get_good(good.pk)
    if cart_item:
        return {
            'good_id': good.pk,
            'already_in_cart': True,
            'text': in_text,
        }
    else:
        return {
            'good_id': good.pk,
            'already_in_cart': False,
            'text': add_text,
        }


@register.inclusion_tag('cart/cart_set_quantity.html')
def cart_set_quantity(good, cart, cart_popup=False):
    cart_item = cart.cached_get_good(good.pk)
    return {
        'good': good,
        'cart_item': cart_item,
        'cart_popup': cart_popup,
    }
