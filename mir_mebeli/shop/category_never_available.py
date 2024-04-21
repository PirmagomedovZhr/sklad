# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.conf import settings

import models

# кеширование списка товаров, которых никогда нет в наличии


site_cache_prefix = getattr(settings, 'SITE_CACHE_PREFIX', '')
cache_prefix = getattr(settings, 'CATALOG_CACHE_PREFIX', 'catalog_')
cache_duration = getattr(settings, 'CATALOG_CATEGORY_NEVER_AVAILABLE_GOODS_CACHE_DURATION', 20*60) # 20 minutes
cache_key = '%s%s%s' % (site_cache_prefix, cache_prefix, 'never_available_goods_ids')


def _build_list():
    cats = models.Category.objects.filter(never_available=True)
    goods = [[good.pk for good in cat.goods.all()] for cat in cats]
    return list(set([item for sublist in goods for item in sublist]))


def invalidate():
    cache.delete(cache_key)


def get_goods_ids():
    cached_goods = cache.get(cache_key, None)

    if cached_goods is None:
        goods = _build_list()
        cache.set(cache_key, goods, cache_duration)
    else:
        goods = cached_goods

    return goods
