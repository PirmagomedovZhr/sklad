# -*- coding: utf-8 -*-
import struct
import hmac
import hashlib
import random
from datetime import datetime

from django.utils.encoding import smart_unicode, smart_str
from pytils.translit import translify

import conf, forms, models


def pack_key(key):
    """Упаковывает ключ в бинарную строку.
        Аналог php-шного pack('H*', key).
    """
    return struct.pack('16B', *[int(c, 16) for c in (key[i:i+2] for i in xrange(0, len(key), 2))])


def make_nonce(length=32):
    """Генерирует строку, содержащую случайное число в шестнадцатеричном формате."""
    length = max(min(length,32),16) # диапазон [16..32]
    allowed_chars = '0123456789ABCDEF'
    return ''.join([random.choice(allowed_chars) for i in range(length)])


def fix_querydict(post):
    """В переданном QueryDict преобразует значения элементов из вида k:[a,b,c] в k:c."""
    return dict([(k,v) for k,v in post.iteritems()])


def make_msg_str(params):
    """Формирует строку данных в виде, нужном для генерации HMAC.
        Принимает список параметров, из которых нужно создать строку данных.
    """
    empty_value = u'-' # подставить в результат, если параметр не определен (None или строка нулевой длины)
    result = u''
    for p in params:
        if p is not None:
            s = smart_unicode(p)
            if len(s) > 0:
                result += u'%s%s' % (len(s), s,)
            else:
                result += empty_value
        else:
            result += empty_value
    return result


def get_sign(msg):
    """Формирует HMAC (подпись)."""
    key = pack_key(conf.KEY)
    msg = smart_str(msg)
    return hmac.new(key, msg, hashlib.sha1).hexdigest()


def get_pay_form(amount, currency, order_id, desc, backref):
    """Возвращает платежную форму Промсвязьбанка."""
    nonce = make_nonce()

    utc_time = datetime.utcnow()
    timestamp = utc_time.strftime('%Y%m%d%H%M%S')

    # fix params
    order = ('%d' % order_id).zfill(6)
    desc = translify(smart_unicode(desc).strip()[:50])
    merch_name = translify(smart_unicode(conf.MERCH_NAME).strip()[:50])
    email = conf.EMAIL.strip()[:80]
    backref = backref[:250]

    # важен порядок параметров!
    params = [
        amount, currency, order, merch_name, conf.MERCHANT, conf.TERMINAL,
        email, models.PAY_TRTYPE, timestamp, nonce, backref,
    ]
    p_sign = get_sign(make_msg_str(params))

    initial = {
        'AMOUNT': amount, 'CURRENCY': currency, 'ORDER': order, 'DESC': desc,
        'TERMINAL': conf.TERMINAL, 'TRTYPE': models.PAY_TRTYPE,
        'MERCH_NAME': merch_name, 'MERCHANT': conf.MERCHANT, 'EMAIL': email,
        'TIMESTAMP': timestamp, 'NONCE': nonce, 'BACKREF': backref,
        'P_SIGN': p_sign,
    }
    return forms.HiddenPayForm(initial=initial)
