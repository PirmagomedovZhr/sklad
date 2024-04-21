# -*- coding: utf-8 -*-
from . import get_conf


def global_discount_settings(request):
    return {'GLOBAL_DISCOUNT': get_conf()}
