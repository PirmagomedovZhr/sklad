# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.simple import direct_to_template
from django.http import HttpResponse
from django.utils import simplejson as json

from mir_mebeli.shop.models import Good

from wishlist import Wishlist
from utils import WishlistItemDoesNotExist


def _get_wishlist_dict(request, wishlist=None):
    """Вишлист в виде словаря для отдачи аяксом."""
    if not wishlist:
        wishlist = Wishlist(request)

    data = {
        'wishlist': {
            'items_count': wishlist.items_count()
        }
    }
    return data


def wishlist(request):
    """Анонимному пользователю показать его вишлист.
        Иначе редиректить покупателя в его корзину на закладку вишлиста.

        Если пришли аяксом - просто отдать состояние вишлиста.
    """
    if request.is_ajax():
        data = _get_wishlist_dict(request)
        return HttpResponse(json.dumps(data), mimetype='application/json')

    if request.user.is_authenticated():
        return redirect(u'%s#wishlist' % reverse('cart'))

    return direct_to_template(request, 'cms/pages/wishlist.html')


def wishlist_print(request):
    """Версия для печати."""
    return direct_to_template(request, 'cms/pages/wishlist_print.html')


def _redirect_on_non_ajax_action(request):
    try:
        return redirect(request.META['HTTP_REFERER'])
    except KeyError:
        if request.user.is_authenticated():
            return redirect(u'%s#wishlist' % reverse('cart'))
        else:
            return redirect('wishlist')


def add_product(request, product_id=None):
    """Добавить товар в вишлист."""
    product = get_object_or_404(Good, pk=product_id)

    wishlist = Wishlist(request, create=True)  # force wishlist creation
    wishlist.add_product(product)

    if request.is_ajax():
        data = _get_wishlist_dict(request, wishlist)
        return HttpResponse(json.dumps(data), mimetype='application/json')

    return _redirect_on_non_ajax_action(request)


def remove_product(request, product_id=None):
    """Удалить товар из вишлиста."""
    product = get_object_or_404(Good, pk=product_id)

    wishlist = Wishlist(request)
    wishlist.remove_product(product)

    if request.is_ajax():
        data = _get_wishlist_dict(request, wishlist)
        return HttpResponse(json.dumps(data), mimetype='application/json')

    return _redirect_on_non_ajax_action(request)
