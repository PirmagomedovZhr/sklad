# -*- coding: utf-8 -*-
from datetime import datetime
import logging

from django.http import HttpResponseForbidden, Http404, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

import api, models, signals, conf


logger = logging.getLogger(__name__)


@require_POST
@csrf_exempt
def result(request):
    """В зависимости от типа операции вызывает нужный обработчик."""
    logger.debug("psbank:result - incoming request - request.POST=%s" % request.POST)
    data = request.POST
    try:
        trtype = int(data['TRTYPE'])
        if trtype == models.PAY_TRTYPE: # оплата товара
            try:
                return pay_result(request)
            except:
                logger.exception("psbank:result - request.POST=%s" % request.POST)
        else:
            raise NotImplementedError()
    except NotImplementedError:
        if conf.DEBUG:
            raise
    return HttpResponseForbidden()


@require_POST
@csrf_exempt
def pay_result(request):
    """Обработчик ответа Банка на запрос проведения оплаты."""
    data = api.fix_querydict(request.POST)
    try:
        # важен порядок параметров!
        params = [
            data['AMOUNT'], data['CURRENCY'], data['ORDER'], data['MERCH_NAME'], data['MERCHANT'], data['TERMINAL'],
            data['EMAIL'], data['TRTYPE'], data['TIMESTAMP'], data['NONCE'], data['BACKREF'], data['RESULT'],
            data['RC'], data['RCTEXT'], data['AUTHCODE'], data['RRN'], data['INT_REF'],
        ]
        p_sign = api.get_sign(api.make_msg_str(params))

        if data['P_SIGN'].upper() != p_sign.upper(): # проверить подпись
            raise Http404(u'Wrong SIGN: %s' % data['P_SIGN'])

        # сохранить операцию
        operation = models.Payment(
            amount = data['AMOUNT'], currency = data['CURRENCY'], order = data['ORDER'], desc = data['DESC'],
            terminal = data['TERMINAL'], trtype = data['TRTYPE'], merch_name = data['MERCH_NAME'],
            merchant = data['MERCHANT'], email = data['EMAIL'],
            timestamp = datetime.strptime(data['TIMESTAMP'], '%Y%m%d%H%M%S'), nonce = data['NONCE'],
            backref = data['BACKREF'], result = data['RESULT'], rc = data['RC'], rctext = data['RCTEXT'],
            authcode = data['AUTHCODE'], rrn = data['RRN'], int_ref = data['INT_REF'], p_sign = data['P_SIGN'],
            name = data['NAME'], card = data['CARD'],
        )
        operation.save()

        # отправить сигнал подписчикам
        signals.pay_received.send(sender=models.Payment, operation=operation)
    except:
        logger.error("psbank:pay_result - something wrong")
        if conf.DEBUG:
            raise
        else:
            return HttpResponseForbidden()
    return HttpResponse('OK%s' % data['ORDER'])
