# -*- coding: utf-8 -*-
import logging

from django.db import models
from django.template import Template, Context
from django.core.urlresolvers import reverse
from django.conf import settings

from utils import truncate_string


logger = logging.getLogger(__name__)

SITE_DOMAIN = getattr(settings, 'SITE_DOMAIN', '')


# типы шаблонов - прочие
REG_THANKS_TEMPLATE = 'reg-thanks' # спасибо за регистрацию

# типы шаблонов - статусы заказов (id такие же, как в модели Order)
ORDER_CANCELED_TEMPLATE = 'order-status-0' # заказ - отмена
ORDER_NEW_TEMPLATE = 'order-status-1' # заказ - новый
ORDER_AWAIT_PAYMENT_TEMPLATE = 'order-status-2' # заказ (наличные) - подтверждён, ожидает оплаты
ORDER_COMPLETING_TEMPLATE = 'order-status-3' # заказ - комплектуется
ORDER_DELIVERING_TEMPLATE = 'order-status-4' # заказ - ожидает доставки
ORDER_DONE_TEMPLATE = 'order-status-5' # заказ - выполнен

ORDER_CARD_AWAIT_PAYMENT_TEMPLATE = 'order-status-6' # заказ (карта) - готов к оплате картой
ORDER_PAID_AWAIT_COMPLETING_TEMPLATE = 'order-status-7' # заказ (карта) - оплачен, ожидает комплектации
ORDER_AWAIT_APPROVAL_TEMPLATE = 'order-status-8' # заказ (карта) - ожидает проверки менеджером
ORDER_CARD_CANCELED_UNPAID_TEMPLATE = 'order-status-9' # заказ (карта) - отмена, не был оплачен в срок


class MessageTemplate(models.Model):
    TEMPLATE_CHOICES = (
        (REG_THANKS_TEMPLATE, u'спасибо за регистрацию'),

        (
            u'Заказ', (
                # оплата картой
                (ORDER_AWAIT_APPROVAL_TEMPLATE, u'(карта) ожидает проверки менеджером'),
                (ORDER_CARD_AWAIT_PAYMENT_TEMPLATE, u'(карта) готов к оплате картой'),
                (ORDER_PAID_AWAIT_COMPLETING_TEMPLATE, u'(карта) оплачен, ожидает комплектации'),
                (ORDER_CARD_CANCELED_UNPAID_TEMPLATE, u'(карта) отменён, не был оплачен в срок'),
                # оплата наличными
                (ORDER_NEW_TEMPLATE, u'(наличные) новый заказ'),
                (ORDER_AWAIT_PAYMENT_TEMPLATE, u'(наличные) подтверждён, ожидает оплаты'),
                # общие статусы заказа
                (ORDER_COMPLETING_TEMPLATE, u'комплектуется'),
                (ORDER_DELIVERING_TEMPLATE, u'ожидает доставки'),
                (ORDER_DONE_TEMPLATE, u'выполнен'),
                (ORDER_CANCELED_TEMPLATE, u'отменён'),
            )
        ),
    )

    template = models.CharField(u'шаблон', max_length=50, choices=TEMPLATE_CHOICES, unique=True)

    subject = models.CharField(u'тема', max_length=100)
    text = models.TextField(u'текст', help_text=(
        u'Для вставки данных в текст письма используйте переменные, заключенные в двойные фигурные скобки:<br>'
        u'<strong>{{ name }}</strong> — имя клиента;<br>'
        u'<strong>{{ login }}</strong> — логин клиента (=email);<br>'
        u'<strong>{{ password }}</strong> — пароль клиента;<br>'
        u'<strong>{{ order_id }}</strong> — номер заказа;<br>'
        u'<strong>{{ order_date }}</strong> — дата заказа;<br>'
        u'<strong>{{ order_pay_till }}</strong> — оплатить до даты;<br>'
        u'<strong>{{ order_pay_link }}</strong> — ссылка на страницу оплаты банковской картой;<br>'
        u'<strong>{{ order_params }}</strong> — параметры заказа.<br>'
        u'<br>'
        u'Для форматирования даты используйте фильтр date. Например:<br>'
        u'<strong>{{ order_pay_till|date:"d.m.Y" }}</strong> — это дата без времени в формате ДД.ММ.ГГГГ<br>'
        u'<strong>{{ order_pay_till|date:"H:i" }}</strong> — это время без даты в формате чч.мм')
    )

    created_at = models.DateTimeField(u'создано', auto_now_add=True)
    updated_at = models.DateTimeField(u'изменено', auto_now=True)

    class Meta:
        verbose_name = u'шаблон письма'
        verbose_name_plural = u'шаблоны писем'
        ordering = ['id']

    def __unicode__(self):
        return self.subject


class Message(models.Model):
    buyer = models.ForeignKey('shop.Buyer', verbose_name=u'покупатель')
    order = models.ForeignKey('shop.Order', verbose_name=u'заказ', blank=True, null=True, default=None)

    to = models.EmailField(u'кому')
    subject = models.CharField(u'тема', max_length=100)
    text = models.TextField(u'текст')

    attempts = models.PositiveIntegerField(u'попытки', default=0)
    sent = models.BooleanField(u'отправленно', default=False)
    sent_at = models.DateTimeField(u'дата отправки', blank=True, null=True, default=None)

    created_at = models.DateTimeField(u'создано', auto_now_add=True)
    updated_at = models.DateTimeField(u'изменено', auto_now=True)

    class Meta:
        verbose_name = u'письмо'
        verbose_name_plural = u'письма'
        ordering = ['-created_at']

    def __unicode__(self):
        return u'%s, %s' % (self.to, truncate_string(self.subject, 50))


def _get_order_params(order):
    s = u''
    s += u'Покупатель: %s.\n' % order.get_full_fio()
    s += u'Адрес для доставки: %s, %s.\n' % (order.city, order.address)
    s += u'Телефон покупателя: %s\n' % order.phone
    s += u'\n'
    s += u'Оплата товаров: %s — %s руб.\n' % (order.get_payment_method(), order.sum)
    s += u'\n'
    s += u'Заказанные позиции:\n'
    for item in order.items.all():
        s += u'%s. %s шт. Цена: %s руб.\n' % (item.good.get_name(), item.count, item.price)
    return s.strip()


def send_mail(template, buyer, order=None, **kwargs):
    """Сгенерировать текст письма по заданному шаблону и добавить в таблицу сообщений."""
    try:
        _msg_templates = MessageTemplate.objects.filter(template__iexact=template).order_by('-created_at')
        msg_template = _msg_templates[0]
        if len(_msg_templates) > 1:
            logger.warning('send_mail - Found multiple templates: %s. Using latest one.' % template)
    except IndexError:
        logger.error('send_mail - Template not found: %s.' % template)
        return False

    d = {
        'buyer': buyer,
        'name': buyer.get_full_name(),
        'login': buyer.email,
        'password': kwargs.get('password'),
        'order': order,
    }

    if order:
        d['order_id'] = order.pk
        d['order_date'] = order.create_date
        d['order_pay_till'] = order.pay_till
        d['order_pay_link'] = '%s%s' % (SITE_DOMAIN, reverse('shop-order-go-bank', args=[order.pk]))
        d['order_params'] = _get_order_params(order)

    t = Template(u'{%% autoescape off %%}%s{%% endautoescape %%}' % msg_template.text)
    c = Context(d)
    txt = t.render(c)

    Message.objects.create(
        buyer=buyer,
        order=order,
        to=buyer.email,
        subject=msg_template.subject,
        text=txt
    )

    return True
