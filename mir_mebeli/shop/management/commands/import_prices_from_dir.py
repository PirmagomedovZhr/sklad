# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime
import logging

from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings

from shop.models import ImportPrices


logger = logging.getLogger('import_prices')

SHOP_SETTINGS = getattr(settings, 'SHOP_SETTINGS')
FROM_DIR = SHOP_SETTINGS['IMPORT_PRICES_FROM_DIR']
FROM_FILENAME = SHOP_SETTINGS['IMPORT_PRICES_FROM_FILENAME']


class Command(BaseCommand):
    help = u'Импорт цен из директории.'

    def handle(self, *args, **options):
        fname = os.path.join(FROM_DIR, FROM_FILENAME)

        if not (os.path.isfile(fname) and os.access(fname, os.R_OK)):
            return

        try:
            with open(fname, 'rb') as f:
                def _make_filename(filename):
                    name, ext = os.path.splitext(filename)
                    return '%s_%s%s' % (name, datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f'), ext,)

                obj = ImportPrices()
                obj.is_robot = 'norobot' not in args
                obj.file.save(_make_filename(FROM_FILENAME), File(f), save=True)

                logger.info('Done importing.')

            os.remove(fname)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            py_fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.error(u'%s: %s (%s:%s)' % (e.__class__.__name__, e, py_fname, exc_tb.tb_lineno,))
