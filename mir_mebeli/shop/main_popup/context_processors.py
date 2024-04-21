# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from .conf import get_conf


def main_popup_settings(request):
    """Добавляет словарь с настройками про главный попап.
        Если период показа прошел или если попап отключен, то ничего не добавляет.
    """
    # для теста
    #request.session['main_popup_last_time'] = datetime.now() - timedelta(days=1)

    _settings = get_conf()

    if not _settings['ENABLED'] or _settings['EXPIRED']:
        return {}

    show_today = True
    last_time = request.session.get('main_popup_last_time')
    if last_time:
        # показывать раз в сутки
        if datetime.now() < last_time + timedelta(days=1):
            show_today = False

    request.session['main_popup_last_time'] = datetime.now()
    _settings['SHOW_TODAY'] = show_today

    return {'MAIN_POPUP': _settings}
