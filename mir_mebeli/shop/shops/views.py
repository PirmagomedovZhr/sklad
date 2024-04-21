# -*- coding: utf-8 -*-
from django.utils.text import normalize_newlines
from django.shortcuts import get_object_or_404

from cms.utils import auto_render
from mir_mebeli.shop.models import Shop


def get_geo(shop):
    """Вытаскивает geo данные из параметров магазина."""
    geo = {
        'region': '',
        'city': '',
        'addr': shop.address.strip(),
        'full_addr': '',
    }

    if shop.region == '1': # мурманск
        geo['city'] = u'г.Мурманск'
    else:
        for name in normalize_newlines(shop.name).split('\n'):
            if u'г.' in name:
                geo['city'] = name.strip()
                break

    if shop.region == '2': # область
        geo['region'] = u'Мурманская область'

    geo['full_addr'] = u", ".join(((geo['region'], geo['city'], geo['addr'])))

    return geo


@auto_render
def root(request):
    return 'cms/pages/shops.html', {
        'shops': {
            'murmansk': Shop.objects.filter(region='1', display=True),
            'murmansk_region': Shop.objects.filter(region='2', display=True),
            'other_region': Shop.objects.filter(region='3', display=True),
        }
    }

@auto_render
def shop(request, shop=None):
    shop = get_object_or_404(Shop, slug=shop)

    return 'cms/pages/shop.html', {
        'shops': {
            'murmansk': Shop.objects.filter(region='1', display=True),
            'murmansk_region': Shop.objects.filter(region='2', display=True),
            'other_region': Shop.objects.filter(region='3', display=True),
        },
        'shop': shop,
        'geo': get_geo(shop),
    }
