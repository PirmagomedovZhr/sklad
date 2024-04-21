# -*- coding: utf-8 -*-
from datetime import datetime

from django.conf import settings


def get_conf():
    _settings = settings.MAIN_POPUP_SETTINGS
    conf = {
        'ENABLED': _settings['ENABLED'],
        'PERIOD_END': _settings['PERIOD_END'],
        'EXPIRED': _settings['PERIOD_END'] < datetime.now(),
    }
    return conf
