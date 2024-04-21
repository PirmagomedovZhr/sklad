# -*- coding: utf-8 -*-
from datetime import datetime

from django.core.management.base import BaseCommand

from shop.models import Order


class Command(BaseCommand):
    """(карта) Отменить заказы, не оплаченные в срок."""

    def handle(self, *args, **options):
        orders = Order.objects.filter(
            payment_method=Order.CARD_PAYMENT_METHOD,
            status=Order.CARD_AWAIT_PAYMENT_STATUS,
            pay_till__lt=datetime.now()
        )
        # сохранить каждый заказ отдельно, чтобы сработал post_save сигнал
        for order in orders:
            # дополнительно проверить, что этот заказ еще не оплачивали картой
            if not order.is_psbank_payment():
                order.card_cancel_unpaid()
                order.save()
