# -*- coding: utf-8 -*-
import sys
import os
from optparse import make_option

from django.core.management.base import BaseCommand

import xlrd

from shop.models import Good


class Command(BaseCommand):
    help = u'Исправление артикулов по переданному прайсу.'
    args = '/path/to/prices.xls'

    option_list = BaseCommand.option_list + (
        make_option('--dry', action='store_true', dest='dry_run',
            default=False, help='Performs a dry run. Does not change anything.'),
    )

    def handle(self, *args, **options):
        fname = args[0] if args else None

        if not fname or (not (os.path.isfile(fname) and os.access(fname, os.R_OK))):
            sys.stderr.write("File not found or is not readable.")
            return

        dry_run = options.get('dry_run', False)

        IDX_ARTICUL = 0

        book = xlrd.open_workbook(fname)
        sh = book.sheet_by_index(0)

        # кешировать артикулы всех товаров
        articuls_cache = Good.objects.values_list('articul', flat=True)

        # уже сохраненные новые артикулы
        updated_articuls = set()

        for rx in xrange(sh.nrows):
            row = sh.row(rx)

            try:
                xls_articul = u'%d' % int(row[IDX_ARTICUL].value)
            except ValueError:
                xls_articul = None

            # пропустить строку если:
            # 1) не задан артикул
            # 2) длина артикула не равна 16
            # 3) товар с таким артикулом уже есть на сайте (значит артикул не менялся)
            # 4) новый артикул уже обрабатывался
            if not xls_articul or len(xls_articul) != 16 or xls_articul in articuls_cache or xls_articul in updated_articuls:
                continue

            # отрезать ведущую '1', потом обрать из начала артикула все '0' и пробелы
            good_old_articul = xls_articul[1:].lstrip().lstrip('0')

            goods = Good.objects.filter(articul__iexact=good_old_articul)
            for good in goods:
                print '%s, %s, %d, %s' % (xls_articul, good.articul, good.pk, good.name)
                if not dry_run:
                    good.articul = xls_articul
                    good.save()
                updated_articuls.add(xls_articul)

        print 'Goods updated =', len(updated_articuls)
