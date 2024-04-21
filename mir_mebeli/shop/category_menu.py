# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.conf import settings

from models import Category


site_cache_prefix = getattr(settings, 'SITE_CACHE_PREFIX', '')
cache_prefix = getattr(settings, 'CATALOG_CACHE_PREFIX', 'catalog_')
cache_duration = getattr(settings, 'CATALOG_CATEGORY_MENU_CACHE_DURATION', 20*60) # 20 minutes
cache_key = '%s%scategory_menu' % (site_cache_prefix, cache_prefix)


def _build_menu():
    #cats = Category.objects.filter(basic=True, count_all__gt=0, hidden=False).order_by('order', 'name')
    cats = Category.objects.filter(basic=True, hidden=False).order_by('order', 'name')

    for cat in cats:
        cat.children = []

        # attach sub categories
        #cat.children += cat.get_descendants().filter(count_all__gt=0, hidden=False).order_by('order', 'name')
        cat.children += cat.get_descendants().filter(hidden=False).order_by('order', 'name')

    return cats


def _mark_selected(request, cats):
    for cat in cats:
        cat_url = cat.get_absolute_url()
        if cat_url == request.path[:len(cat_url)]:
            cat.selected = True
            break


def get_menu(request):
    cached_cats = cache.get(cache_key, None)

    if cached_cats:
        cats = cached_cats
    else:
        cats = _build_menu()
        cache.set(cache_key, cats, cache_duration)

    _mark_selected(request, cats)

    return cats
