# -*- coding: utf-8 -*-
from datetime import datetime

from django.conf import settings


def get_conf():
    _settings = settings.GLOBAL_DISCOUNT_SETTINGS
    conf = {
        'ENABLED': _settings['ENABLED'],
        'PERIOD_END': _settings['PERIOD_END'],
        'EXPIRED': _settings['PERIOD_END'] < datetime.now(),
        'PERCENTS': _settings['PERCENTS'],
        'EXCLUDE_CATEGORY_IDS': _settings['EXCLUDE_CATEGORY_IDS'],
    }
    return conf
