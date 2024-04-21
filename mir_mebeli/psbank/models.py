# -*- coding: utf-8 -*-
from django.db import models


# принимаемые валюты
RUR_CURRENCY = u'RUB'
USD_CURRENCY = u'USD'
EUR_CURRENCY = u'EUR'

# результат обработки запроса на операцию
SUCCESS_RESULT = 0
DUB_RESULT = 1
BANK_REJECTED_RESULT = 2
GATEWAY_REJECTED_RESULT = 3

# тип запрашиваемой операции
PAY_TRTYPE = 1
#CANCEL_TRTYPE = 24
#PRE_AUTH_TRTYPE = 0
#FINISH_TRTYPE = 21


class Payment(models.Model):
    """Операция оплаты: ответ банка на запрос проведения оплаты."""

    CURRENCY_CHOICES = (
        (RUR_CURRENCY, u'рубли'),
        (USD_CURRENCY, u'доллары'),
        (EUR_CURRENCY, u'евро'),
    )

    TRTYPE_CHOICES = (
        (PAY_TRTYPE, u'оплата товара'),
#        (CANCEL_TRTYPE, u'отмена оплаты товара'),
#        (PRE_AUTH_TRTYPE, u'предавторизация'),
#        (FINISH_TRTYPE, u'завершение расчётов'),
    )

    RESULT_CHOICES = (
        (SUCCESS_RESULT, u'операция успешно завершена'),
        (DUB_RESULT, u'запрос идентифицирован как повторный'),
        (BANK_REJECTED_RESULT, u'запрос отклонен Банком'),
        (GATEWAY_REJECTED_RESULT, u'запрос отклонен Платежным шлюзом'),
    )

    amount = models.DecimalField(u'Сумма', max_digits=11, decimal_places=2)
    currency = models.CharField(u'Валюта', max_length=3, choices=CURRENCY_CHOICES, default=RUR_CURRENCY)

    order = models.PositiveIntegerField(u'Номер заказа', db_index=True, help_text=u'Уникальный номер заказа')
    desc = models.CharField(u'Описание заказа', max_length=250, default='')

    terminal = models.CharField(u'Терминал', max_length=8, help_text=u'Уникальный номер виртуального терминала Торговой точки.')
    trtype = models.PositiveSmallIntegerField(u'Тип операции', choices=TRTYPE_CHOICES, default=PAY_TRTYPE)
    merch_name = models.CharField(u'Название', max_length=50, help_text=u'Короткое название Торговой точки.')
    merchant = models.CharField(u'Торговая точка', max_length=15, help_text=u'Уникальный номер Торговой точки.')

    email = models.EmailField(u'Эл.почта', default='', help_text=u'Адрес электронной почты Торговой точки.')
    timestamp = models.DateTimeField(u'Дата операции', help_text=u'UTC время проведения операции.')
    nonce = models.CharField(u'Случайное число', max_length=32, help_text=u'В шестнадцатеричном формате.')
    backref = models.URLField(u'URL возврата', max_length=250, default='',
        help_text=u'URL для возврата на сайт Торговой точки после проведения операции.')

    result = models.PositiveSmallIntegerField(u'Результат', choices=RESULT_CHOICES, null=True, blank=True,
        help_text=u'Результат обработки запроса на операцию')

    rc = models.SmallIntegerField(u'RC', null=True, blank=True,
        help_text=u'Respose Code - Код ответа на попытку проведения операции.')
    rctext = models.CharField(u'RCText', max_length=250, default='', blank=True,
        help_text=u'Response Code Text - Расшифровка кода ответа на попытку проведения операции.')

    authcode = models.CharField(u'Код авторизации', max_length=32, default='', blank=True,
        help_text=u'Буквенно-цифровой код, выдаваемый банком, выпустившим карту, в случае успешной попытки проведения операции.')

    rrn = models.CharField(u'RRN', max_length=12, blank=True, default='',
        help_text=u'Retrieval Reference Number - Уникальный идентификатор запроса на списание средств с карты.')
    int_ref = models.CharField(u'Int_Ref', max_length=32, default='', blank=True,
        help_text=u'Internal Reference - Уникальный идентификатор операции на платежном шлюзе.')

    p_sign = models.CharField(u'HMAC ответа банка', max_length=40)

    name = models.CharField(u'Имя держателя карты', max_length=250, default='', blank=True)
    card = models.CharField(u'Номер карты', max_length=250, default='', blank=True,
        help_text=u'Маскированный номер карты.')

    # прочие поля
    created_at = models.DateTimeField(u'Создано', auto_now_add=True)
    updated_at = models.DateTimeField(u'Изменено', auto_now=True)

    class Meta:
        verbose_name = u'Операция с Промсвязьбанком'
        verbose_name_plural = u'Операции с Промсвязьбанком'
        ordering = ('-created_at',)
        permissions = (('can_test_operations', u'Может тестировать Операции с Промсвязьбанком'),)

    def __unicode__(self):
        return u'Заказ № %s, %s.' % (self.order, self.get_trtype_display(),)

    def save(self, *args, **kwargs):
        def _trunc(val, max_len):
            return val[:max_len] if val else val

        self.currency = _trunc(self.currency, 3)
        self.desc = _trunc(self.desc, 250)
        self.terminal = _trunc(self.terminal, 8)
        self.merch_name = _trunc(self.merch_name, 50)
        self.merchant = _trunc(self.merchant, 15)
        self.email = _trunc(self.email, 75)
        self.nonce = _trunc(self.nonce, 32)
        self.backref = _trunc(self.backref, 250)
        self.rctext = _trunc(self.rctext, 250)
        self.authcode = _trunc(self.authcode, 32)
        self.rrn = _trunc(self.rrn, 12)
        self.int_ref = _trunc(self.int_ref, 32)
        self.p_sign = _trunc(self.p_sign, 40)
        self.name = _trunc(self.name, 250)
        self.card = _trunc(self.card, 250)

        super(Payment, self).save(*args, **kwargs)
