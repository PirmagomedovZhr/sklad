# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from shop.models import update_category_counters


class Command(BaseCommand):
    help = u'Обновление счётчиков категорий.'

    def handle(self, *args, **options):
        update_category_counters()
