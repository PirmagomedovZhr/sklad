# -*- coding: utf-8 -*-
import os
import logging
import logging.handlers
from datetime import datetime

# Django settings for mir_mebeli project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
)

MANAGERS = ADMINS

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

SITE_CACHE_PREFIX = 'new_sklad51_'

CMS_CACHE_PREFIX = '%scms-' % SITE_CACHE_PREFIX

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '', # Or path to database file if using sqlite3.
        'USER': '', # Not used with sqlite3.
        'PASSWORD': '', # Not used with sqlite3.
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Moscow'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

gettext = lambda s: s

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public_html/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '5d5lkqhutmctqjk*9h3ghg2va5clr)rly_h!sz*nc5(s-7!xj7'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'cms.middleware.media.PlaceholderMediaMiddleware',
    'cbv.middleware.DeferredRenderingMiddleware',
    'mir_mebeli.guestbook.middelware.XForwardedForMiddleware',
)

ROOT_URLCONF = 'mir_mebeli.urls'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.comments',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',

    'cms',
    'cms.plugins.text',
    'cms.plugins.picture',
    'cms.plugins.link',
    'cms.plugins.file',
    'cms.plugins.snippet',
    'cms.plugins.googlemap',
    'cmsplugin_news',
    'menus',
    'mptt',
    'publisher',
    'pagination',

    'django_extensions',
    'djapian',
    'sorl.thumbnail',
    'pytils',
    'tinymce',
    'endless_pagination',
    'yandex_money',

    'mir_mebeli.teasers',
    'mir_mebeli.vacancies',
    'mir_mebeli.cart',
    'mir_mebeli.wishlist',
    'mir_mebeli.shop',
    'mir_mebeli.guestbook',
    'mir_mebeli.utilities',
    'mir_mebeli.psbank',
    'mir_mebeli.mailing',
    'mir_mebeli.partners',

    'mir_mebeli.captcha',

    'south',  # keep it last
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    "django.core.context_processors.media",
    "cms.context_processors.media",
    'mir_mebeli.cart.context_processors.cart',
    'mir_mebeli.wishlist.context_processors.wishlist',
    'mir_mebeli.shop.context_processors.shop',
    'mir_mebeli.shop.context_processors.catalog_category_menu',
    'mir_mebeli.shop.main_popup.context_processors.main_popup_settings',
    'mir_mebeli.shop.global_discount.context_processors.global_discount_settings',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.csrf',
)

CMS_TEMPLATES = (
    ('cms/pages/index.html', gettext(u'Главная')),
    ('cms/pages/inner.html', gettext(u'Внутренняя')),
    ('cms/pages/contacts.html', u'Контакты + Яндекс.Карта'),
    ('cms/pages/guestbook.html', gettext(u'Гостевая книга')),
    ('partners/partners.html', u'Партнерам'),
)

LANGUAGES = (
    ('ru', gettext('Russian')),
)

CMS_NAVIGATION_EXTENDERS = (
    ('mir_mebeli.shop.shops.utils.get_nodes', gettext('Shops')),
    ('cmsplugin_news.navigation.get_nodes', gettext('News')),
    ('mir_mebeli.vacancies.utils.get_nodes', gettext('Vacancy')),
)

CMS_APPLICATIONS_URLS = (
    ('mir_mebeli.guestbook.urls', 'Guestbook'),
    ('mir_mebeli.shop.shops.urls', 'Shops'),
    ('mir_mebeli.vacancies.urls', 'Vacancy'),
    ('mir_mebeli.partners.urls', 'Partners'),
    ('cmsplugin_news.urls', 'News'),
)

CMS_PLACEHOLDER_CONF = {
    'content': {'name': gettext(u"контент")},
    'shop-news': {'name': gettext(u"новости")},
    'search-info': {'name': gettext(u"текст для поисковых систем")},
    'teaser-left': {'name': gettext(u"левый тизер в контенте")},
    'teaser-right': {'name': gettext(u"правый тизер в контенте")},
}

CMS_SEO_FIELDS = True
CMS_REDIRECTS = True

CMS_TEMPLATE_INHERITANCE = False

TINYMCE_DEFAULT_CONFIG = {
    'theme': "advanced",
    'plugins': "autolink,lists,table,paste",

    'theme_advanced_buttons1': ",bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,formatselect,fontselect,fontsizeselect,|,forecolor,backcolor,styleprops,removeformat,styleselect",
    'theme_advanced_buttons2': "cut,copy,paste,pastetext,pasteword,|,search,replace,|,bullist,numlist,|,outdent,indent,blockquote,|,undo,redo,|,link,unlink,anchor,image,images,cleanup,help,code,|,charmap,insertdate,inserttime",
    'theme_advanced_buttons3': "tablecontrols,|,hr,removeformat,visualaid,|,sub,sup,|,fullscreen,preview,print,",
    'theme_advanced_toolbar_location': "top",
    'theme_advanced_toolbar_align': "left",
    'theme_advanced_statusbar_location': "bottom",
    'theme_advanced_resizing': True,

    'convert_urls': False,
    'relative_urls': False,
    'remove_script_host': False,
}

NOCAPTCHA = True
RECAPTCHA_PUBLIC_KEY = u'define'
RECAPTCHA_PRIVATE_KEY = u'define'

DJAPIAN_DATABASE_PATH = MEDIA_ROOT + '../djapian_spaces/'
DJAPIAN_STEMMING_LANG = "ru"

SHOP_SETTINGS = {
    'FALLBACK_EMAILS': ['alexander.time@gmail.com', 'lu@air51.ru'],
    'CHIEF_EMAILS': ['alexander.time@gmail.com', 'lu@air51.ru'],

    'EMAIL_SENDER': 'robot@sklad51.ru',
    'EMAIL_GROUP': 1, # отправить письмо членам группы `менеджер`
    'ORDER_PAID_EMAIL_SUBJ': u'Оплата заказа на сайте sklad51.ru',

    # префикс урл-а для возврата на сайт после проведения операции в Промсвязьбанке: к нему добавится номер заказа
    'PSBANK_BACK_URL': 'http://sklad51.ru/order/done/',

#    'KUHNI_NA_ZAKAZ_CATEGORY_ID': 111,

    'IMPORT_PRICES_FROM_DIR': '/ftp/prices',
    'IMPORT_PRICES_FROM_FILENAME': 'prices_td.xls',
}

MAILING_MAX_ATTEMPTS = 2
MAILING_FROM_EMAIL = 'robot@sklad51.ru'

PSBANK_SETTINGS = {
    'TERMINAL': 79036786,
    'MERCHANT': 790367686219999,
    'KEY': 'C50E41160302E0F5D6D59F1AA3925C45',

    'MERCH_NAME': u'Склад51',
    'EMAIL': 'andrey.goo@gmail.com',

    'TEST_MODE': True,
    'DEBUG': True,
}

MAIN_POPUP_SETTINGS = {
    'ENABLED': False,
    'PERIOD_END': datetime(2017, 1, 1),  # подольше
}

GLOBAL_DISCOUNT_SETTINGS = {
    'ENABLED': False,
    'PERIOD_END': datetime(2017, 1, 1),  # подольше

    'PERCENTS': [  # сумма заказа, процент
        (10000, 5),
        (20000, 7),
        (40000, 10),
        (70000, 12),
        (100000, 15),
    ],

    'EXCLUDE_CATEGORY_IDS': set([
        # Диваны
        169, 197, 95, 158, 125,
        # Кресла
        175, 227, 217, 170,
        # Кровати
        121, 152, 215,
        # Матрасы
        183, 153, 122,
        # Ортопедические основания
        123, 184, 154,
        # Пуфы
        225, 228,
        # Угловые диваны
        224, 229,
    ]),
}

SITE_DOMAIN = 'sklad51.ru'

# setup loggers
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'log')
LOG_FORMATTER = logging.Formatter('%(asctime)s %(levelname)s - %(name)s - %(message)s')

def _setup_logger(name, filename, level=logging.DEBUG, formatter=LOG_FORMATTER, propagate=True, max_bytes=10*1024*1024, backup_count=10):
    try:
        logger = logging.getLogger(name)
        logger.setLevel(level)
        handler = logging.handlers.RotatingFileHandler(
            os.path.join(LOG_DIR, filename), maxBytes=max_bytes, backupCount=backup_count)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = propagate
    except IOError as e:
        print u"WARNING! Couldn't create log.", e


if not hasattr(logging, "setup_done"):
    _setup_logger(None, 'main.log') # root logger
    _setup_logger('psbank', 'psbank.log', propagate=False)
    _setup_logger('import_prices', 'import_prices.log', propagate=False)
    _setup_logger('partners', 'partners.log', propagate=False)
    _setup_logger('mailing', 'mailing.log', propagate=False)
    _setup_logger('yandex_money', 'yandex_money.log', propagate=False)
    _setup_logger('sorl.thumbnail', 'sorl-thumbnail.log', propagate=False, max_bytes=5*1024*1024, backup_count=1)
    logging.setup_done = True # hack to prevent double init

SOUTH_LOGGING_ON = False

SERVER_EMAIL = 'sklad51@localhost'

LOGIN_URL = '/register-and-login/'

THUMBNAIL_UPSCALE = False
THUMBNAIL_CACHE_TIMEOUT = 3600  # cache for 1 hour then get from db
THUMBNAIL_PRESERVE_FORMAT = True

ENDLESS_PAGINATION_ORPHANS = 2
ENDLESS_PAGINATION_LOADING = """<img src="/media/images/loading-small.gif" alt="загрузка товаров" />"""

YANDEX_MONEY_DEBUG = True
YANDEX_MONEY_SCID = 12345
YANDEX_MONEY_SHOP_ID = 56789
YANDEX_MONEY_SHOP_PASSWORD = 'password'
YANDEX_MONEY_FAIL_URL = 'http://sklad51.ru/order/done/'
YANDEX_MONEY_SUCCESS_URL = 'http://sklad51.ru/order/done/'
YANDEX_MONEY_PAYMENT_URL = 'https://demomoney.yandex.ru/eshop.xml'
# информировать о случаях, когда модуль вернул Яндекс.Кассе ошибку
YANDEX_MONEY_MAIL_ADMINS_ON_PAYMENT_ERROR = True
YANDEX_ALLOWED_PAYMENT_TYPES = ('AC')

try:
    from local_settings import *
except ImportError:
    pass
