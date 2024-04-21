# -*- coding: utf-8 -*-

from mir_mebeli.shop.models import Shop

def get_nodes(request):
    return list(Shop.objects.all())

