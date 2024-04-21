# -*- coding: utf-8 -*-
from django.conf import settings

# настройки

conf = settings.PSBANK_SETTINGS

TERMINAL = conf['TERMINAL'] # уникальный номер виртуального терминала торговой точки
MERCHANT = conf['MERCHANT'] # уникальный номер торговой точки
KEY = conf['KEY'] # секретный ключ для генерации HMAC запросов

MERCH_NAME = conf['MERCH_NAME'] # короткое название торговой точки
EMAIL = conf['EMAIL'] # адрес эл. почты Торговой  точки

# тестовый режим
TEST_MODE = conf.get('TEST_MODE', False)

# url, куда отправлять пользователя для произведения им оплаты
PAYMENT_URL = 'https://3ds.payment.ru/cgi-bin/cgi_link'
if TEST_MODE:
    PAYMENT_URL = 'http://193.200.10.117:8080/cgi-bin/cgi_link'

# режим отладки
DEBUG = conf.get('DEBUG', False)
