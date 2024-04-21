# -*- coding: utf-8 -*-
from django import template


register = template.Library()


@register.inclusion_tag('wishlist/add_to_wishlist_link.html')
def add_to_wishlist_link(good, wishlist):
    if wishlist.wishlist and wishlist.wishlist.get_item(product=good):
        return {
            'good_id': good.pk,
            'already_in_wishlist': True,
            'title': '',
        }
    else:
        return {
            'good_id': good.pk,
            'already_in_wishlist': False,
            'title': '',
        }
