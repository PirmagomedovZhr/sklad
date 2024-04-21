# -*- coding: utf-8 -*-
import os
from datetime import datetime, timedelta
from time import time
import re
from random import choice, random
import hashlib
from collections import OrderedDict
import logging

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.db.models.signals import m2m_changed, post_save, pre_delete, pre_save, post_delete
from django.db.models import F, Count #, Avg, Max, Min
from django.contrib.auth.models import User, UserManager
from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from django.core.mail import send_mail, mail_admins
from django.http import Http404
from django.utils.encoding import smart_unicode
from django.db import connection, transaction
from django.utils.functional import curry
from django.conf import settings

from pytils.translit import slugify
import mptt
import xlrd

import psbank
import mailing
import category_never_available
from utilities import uniquify_list

from yandex_money.forms import PaymentForm
from yandex_money.models import Payment

from .good_types import GOOD_TYPE_CHOICES, GOOD_TYPES, GOOD_FIELDS, DEFAULT_GOOD_FIELDS


mailing_logger = logging.getLogger('mailing')


DEBUG_PRICE_LIST = getattr(settings, 'SHOP_DEBUG_PRICE_LIST', False)
SHOP_SETTINGS = getattr(settings, 'SHOP_SETTINGS')


def update_category_counters():
    cursor = connection.cursor()
    sql = (
        'UPDATE shop_category as cat SET '
            'count_all = (select count(*) from shop_good where category_id=cat.id), '
            'count_online = (select count(*) from shop_good '
                'where category_id=cat.id and shop_good.is_available is true);'
    )
    cursor.execute(sql)
    transaction.commit_unless_managed()


class Category(models.Model):
    def _make_upload_path(instance, filename):
        """Generates upload path for FileField"""
        name, ext = os.path.splitext(filename)
        return u"categories/%s%s" % (slugify(instance.name), ext,)

    parent = models.ForeignKey("self", verbose_name=u'родительская категория', default=None, blank=True, null=True)
    parent.category_no_leaf_nodes_filter_spec = True

    good_type = models.CharField(u'тип товаров', max_length=50, choices=GOOD_TYPE_CHOICES, blank=True, default='',
        db_index=True)

    name = models.CharField(u"название", max_length=80, db_index=True)
    name_in_xls = models.CharField(u"название в прайс-листе", max_length=80, blank=True, null=True)
    description = models.TextField(u"описание", blank=True, null=True)
    image = models.ImageField(u"картинка", upload_to=_make_upload_path, blank=True, null=True)
    basic = models.BooleanField(u"основная")
    slug = models.SlugField(max_length=80, blank=True, null=True, editable=False)
    path = models.CharField(editable=False, max_length=250, default='')
    count_all = models.PositiveIntegerField(u'товаров (всего)', editable=False, default=0)
    count_online = models.PositiveIntegerField(u'товаров (online)', editable=False, default=0)
    meta_description = models.TextField(u'meta description', max_length=255, blank=True, default='',
        help_text=u'Описание страницы для поиска.')
    meta_keywords = models.CharField(u"ключевые слова", max_length=100, blank=True, null=True)
    search_title = models.CharField(u"заголовок для поиска", max_length=80, blank=True, null=True)
    search_text = models.TextField(u"текст для поиска", blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    order = models.CharField(u'сортировка', max_length=20, blank=True, null=True, default=None, db_index=True)

    hidden = models.BooleanField(u'скрыта', default=False)
    never_available = models.BooleanField(u'товаров никогда нет в наличии', default=False,
        help_text=u'У товаров, входящих в эту рубрику, можно только запросить срок доставки. А добавить в корзину - нельзя.')

    class Meta:
        verbose_name = u"Категория"
        verbose_name_plural = u"Категории"
        ordering = ('order', 'name',)

    def __unicode__(self):
        return u"%s" % self.name

    def get_absolute_url(self):
        return reverse('category_view', kwargs={'category_path': self.path})

    def get_menu_title(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        # path = parent-slug/slug
        slugs = []
        if self.parent:
            slugs.append(self.parent.path)
        slugs.append(self.slug)
        self.path = '/'.join(slugs)
        try:
            if not self.order.strip():
                self.order = None
            else:
                self.order = self.order.strip()
        except AttributeError:
            pass
        super(Category, self).save(*args, **kwargs)

try:
    mptt.register(Category)
except mptt.AlreadyRegistered:
    pass


def category_post_save(sender, instance, created, **kwargs):
    for subcat in instance.get_descendants():
        subcat.save()  # update children path
    category_never_available.invalidate()

post_save.connect(category_post_save, sender=Category, dispatch_uid='shop.category_post_save')


def category_post_delete(sender, instance, **kwargs):
    category_never_available.invalidate()

post_delete.connect(category_post_delete, sender=Category, dispatch_uid='shop.category_post_delete')


class Good(models.Model):
    def _make_upload_path(instance, filename):
        """Generates upload path for FileField"""
        root = u'categories'
        no_category_root = u'other'
        try:
            return os.path.join(root, slugify(instance.category.name), filename)
        except (AttributeError, ValueError) as e:
            return os.path.join(root, no_category_root, filename)

    category = models.ForeignKey(Category, related_name='goods', verbose_name=u'категория', blank=True, null=True)
    category.category_filter_spec = True

    name = models.CharField(u"название", max_length=80)
    display_name = models.CharField(u'название для отображения', max_length=80, blank=True, default='')
    articul = models.CharField(u"артикул", max_length=20, blank=True, null=True)
    short_description = models.TextField(u'краткое описание', blank=True, default='')
    description = models.TextField(u"описание", blank=True, null=True)
    price = models.DecimalField(u'цена', max_digits=7, decimal_places=0, default=0)
    sale = models.DecimalField(u"процент скидки", max_digits=5, decimal_places=2, blank=True, null=True)
    image = models.ImageField(u"картинка", upload_to=_make_upload_path, blank=True, null=True)
    new = models.BooleanField(u"новинка", default=False)
    date = models.DateField(u"дата добавления", auto_now_add=True, blank=True, null=True)
    special = models.BooleanField(u"распродажа", default=False)
    is_available = models.BooleanField(u'наличие', blank=True, default=True)

    producer = models.CharField(u'производитель', max_length=80, blank=True, default='')
    brand = models.CharField(u'бренд', max_length=255, blank=True, default='')
    weight = models.CharField(u'масса', max_length=20, blank=True, default='')
    color = models.CharField(u'цвет', max_length=80, blank=True, default='')
    usage_area = models.CharField(u'область применения', max_length=255, blank=True, default='')
    expense = models.CharField(u'расход материала', max_length=255, blank=True, default='')
    amount = models.CharField(u'кол-во в упаковке', max_length=20, blank=True, default='')
    dims = models.CharField(u'размер', max_length=20, blank=True, default='', help_text=u"ДхВхГ, мм")

    units = models.CharField(u'ед. изм.', max_length=20, blank=True, default='', help_text=u"Единица измерения.")

    class Meta:
        verbose_name = u"товар"
        verbose_name_plural = u"товары"
        ordering = ['-is_available', '-price', '-id']

    def __unicode__(self):
        return self.get_name()

    def get_absolute_url(self, base=None):
        try:
            return reverse('good_view', kwargs={'category_path': base or self.category.path, 'good_id': self.pk})
        except AttributeError:
            return None

    def get_name(self):
        """Название товара."""
        return self.display_name or self.name
    get_name.short_description = u'Название'

    def get_menu_title(self):
        return self.get_name()

    def is_new(self):
        if self.new: return True
        return (datetime.now() - self.date).days > 14

    def get_custom_fields(self):
        """Поля, относящиеся к типу товара, и их значения.
            Тип товара берётся из категории, в которую включен товар.
            Если тип товара не выбран, возвращает поля по умолчанию.
        """
        d = OrderedDict()
        if self.category_id and self.category.good_type:
            try:
                for key in GOOD_TYPES[self.category.good_type]['fields']:
                    d[key] = {
                        'name': GOOD_FIELDS.get(key) or key,
                        'value': getattr(self, key, None),
                    }
                return d
            except KeyError:
                return None
        else:
            for key in DEFAULT_GOOD_FIELDS:
                d[key] = {
                    'name': GOOD_FIELDS.get(key) or key,
                    'value': getattr(self, key, None),
                }
            return d

    @property
    def categories_count(self):
        """Кол-во категорий, в которые входит товар: 0 или 1."""
        if getattr(self, '_cache_categories_count', None) is None:
            self._cache_categories_count = 1 if self.category_id else 0
        return self._cache_categories_count

    @property
    def any_hidden_category(self):
        """Скрыта ли категория, в которую входит товар."""
        if getattr(self, '_cache_any_hidden_category', None) is None:
            try:
                self._cache_any_hidden_category = self.category.hidden
            except AttributeError:
                self._cache_any_hidden_category = False
        return self._cache_any_hidden_category

    @property
    def unit_price(self):
        try:
            return '%f' % self.price
        except:
            return 0

    @property
    def is_available_for_order(self):
        return self.is_available

    @property
    def is_never_available(self):
        """Возвращает True, если товар входит в категорию, у которой товары принудительно выставлены так,
            будто их никогда нет в наличии.
        """
        return self.pk in category_never_available.get_goods_ids()

    @property
    def is_really_available(self):
        return not self.is_never_available and self.is_available and self.price > 0

    @property
    def price_with_discount(self):
        return int(round(self.price - self.price * (self.sale / 100)))

    def colours(self):
        return {'list': self.colour.all(), 'multi': self.colour.filter(second_color__isnull=False).count() > 0,}

    def get_parent(self):
        return None

    def set_parent(self, parent):
        pass

    parent = property(get_parent, set_parent)

    def get_parent_id(self):
        return None

    def set_parent_id(self, parent):
        pass

    parent_id = property(get_parent_id, set_parent_id)

try:
    mptt.register(Good)
except mptt.AlreadyRegistered:
    pass


# TODO remove or rewrite to update Category counters
#def m2m_changed_handler(sender, instance, action, reverse, model, pk_set, **kwargs):
#    """Обработка событий изменения m2m связи товар-категория."""
#    if action in ['post_add', 'post_remove', 'post_clear']:
#        category_never_available.invalidate()
#
#    if not pk_set and 'pre_clear' != action:
#        return
#
#    if 'pre_add' == action:
#        # добавить родителей добавляемых категорий
#        for category in Category.objects.filter(pk__in=pk_set, parent__isnull=False).exclude(parent__pk__in=pk_set):
#            # print '-- add parent', category.parent.pk
#            instance.categories.add(category.parent)
#
#    elif 'post_add' == action:
#        Category.objects.filter(pk__in=pk_set).update(count_all=F('count_all') + 1)
#        if instance.is_available_for_order:
#            Category.objects.filter(pk__in=pk_set).update(count_online=F('count_online') + 1)
#
#    elif 'pre_remove' == action:
#        Category.objects.filter(pk__in=pk_set, count_all__gt=0).update(count_all=F('count_all') - 1)
#        if instance.is_available_for_order:
#            Category.objects.filter(pk__in=pk_set, count_online__gt=0).update(count_online=F('count_online') - 1)
#
#    elif 'pre_clear' == action:
#        instance.categories.filter(count_all__gt=0).update(count_all=F('count_all') - 1)
#        if instance.is_available_for_order:
#            instance.categories.filter(count_online__gt=0).update(count_online=F('count_online') - 1)
#
#m2m_changed.connect(m2m_changed_handler, sender=Good.categories.through, dispatch_uid='shop.good.m2m_changed')


# TODO remove or rewrite to update Category counters
#def pre_delete_good_handler(sender, instance, **kwargs):
#    """Перед удалением товара."""
#    instance.categories.filter(count_all__gt=0).update(count_all=F('count_all') - 1)
#    if instance.is_available_for_order:
#        instance.categories.filter(count_online__gt=0).update(count_online=F('count_online') - 1)
#
#pre_delete.connect(pre_delete_good_handler, sender=Good, dispatch_uid='shop.good.pre_delete')


class Color(models.Model):
    def _make_upload_path(instance, filename):
        """Generates upload path for FileField"""
        return u"colors/%s" % filename

    name = models.CharField(u"название", max_length=20)
    image = models.ImageField(u"картинка", upload_to=_make_upload_path, blank=True, null=True)

    class Meta:
        verbose_name = u"цвет"
        verbose_name_plural = u"цвета"

    def __unicode__(self):
        return u"%s" % self.name


class Colour(models.Model):
    good = models.ForeignKey(Good, related_name="colour", verbose_name=u"товар")
    first_color = models.ForeignKey(Color, related_name="first_color", verbose_name=u"цвет корпуса")
    second_color = models.ForeignKey(Color, related_name="second_color", blank=True, null=True, verbose_name=u"цвет фасада")

    class Meta:
        verbose_name = u"расцветка"
        verbose_name_plural = u"расцветки"

    def get_second_colour(self):
        return self.second_color or self.first_color


class Shop(models.Model):
    REGION_CHOICES = (
        ('1', u'Мурманск'),
        ('2', u'Мурманская область'),
        ('3', u'Другие регионы'),
    )

    def _make_upload_path(instance, filename):
        """Generates upload path for FileField"""
        return u"shops/%s" % filename

    name = models.TextField(u"название")
    name_in_xls = models.CharField(u"название в прайс-листе", max_length=50, blank=True, null=True)
    address = models.CharField(u"адрес", max_length=80, blank=True, null=True)
    region = models.CharField(u"регион", max_length=5, choices=REGION_CHOICES)
    image = models.ImageField(u"картинка", upload_to=_make_upload_path, blank=True, null=True)
    contact = models.TextField(u"контактная информация", blank=True, null=True)
    mode = models.CharField(u"режим работы", max_length=80, blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    display = models.BooleanField(u"показывать в магазинах", default=True)
    online = models.BooleanField(u"онлайн заказ", default=False)

    class Meta:
        verbose_name = u"магазин"
        verbose_name_plural = u"магазины"

    def __unicode__(self):
        return u"%s: %s" % (self.name, self.address,)

    def get_absolute_url(self):
        return reverse('shop_view', kwargs={'shop': self.slug,})

    def get_menu_title(self):
        return self.name

    def save(self):
        if not self.slug:
            try:
                groups = re.search(u'(?:«(.*?)»|"(.*?)")', self.name).groups()
                base_slug = slugify(groups[0] or groups[1] or self.name)
            except:
                base_slug = slugify(self.name)
            slug = base_slug
            collation = True
            i = 1
            while collation:
                if self.id:
                    collation = Shop.objects.filter(slug=slug).exclude(id=self.id)
                else:
                    collation = Shop.objects.filter(slug=slug)
                if collation:
                    i += 1
                    slug = '%s_%s' % (base_slug, i)
            self.slug = slug
        super(Shop, self).save()

    def first_contact(self):
        return re.split("\n+", self.contact)[0]

    def get_parent(self):
        return None

    def set_parent(self, parent):
        pass

    parent = property(get_parent, set_parent)

    def get_parent_id(self):
        return None

    def set_parent_id(self, parent):
        pass

    parent_id = property(get_parent_id, set_parent_id)

try:
    mptt.register(Shop)
except mptt.AlreadyRegistered:
    pass


class BuyerManager(UserManager):
    def create_buyer(self, email, password):
        username = hashlib.sha1(u'%s%s' % (email, random())).hexdigest()[:30]
        user = self.create_user(username=username, email=email, password=password)
        user.save()
        return user


class Buyer(User):
    mid_name = models.CharField(u'Отчество', max_length=30, default='', blank=True)

    city = models.ForeignKey('City', verbose_name=u'город', null=True, blank=True, default=None)
    address = models.CharField(u'Адрес', max_length=100, default='', blank=True)
    phone = models.CharField(u'Телефон', max_length=20, default='', blank=True)

    subscribe = models.BooleanField(u'Присылать предложения', default=False, blank=True)

    objects = BuyerManager()

    class Meta:
        verbose_name = u"покупатель"
        verbose_name_plural = u"покупатели"

    def __unicode__(self):
        return (u'%s  %s' % (self.phone, self.email,)).strip() or self.username

    def get_full_name(self):
        return (u'%s %s %s' % (self.last_name, self.first_name, self.mid_name)).strip()


class City(models.Model):
    name = models.CharField(u'название', max_length=50, unique=True)
    ordering = models.PositiveIntegerField(u'сортировка', null=True, blank=True)

    class Meta:
        verbose_name = u'город'
        verbose_name_plural = u'города'
        ordering = ['ordering', 'name',]

    def __unicode__(self):
        return self.name


class OrderManager(models.Manager):
    def get_unfinished_orders_list(self):
        """Выбрать только незавершённые заказы."""
        statuses = (Order.NEW_STATUS, Order.AWAIT_PAYMENT_STATUS, Order.COMPLETING_STATUS, Order.DELIVERING_STATUS,
            Order.PAID_AWAIT_COMPLETING_STATUS, Order.AWAIT_APPROVAL_STATUS, Order.CARD_AWAIT_PAYMENT_STATUS)
        return self.filter(status__in = statuses).order_by('-pk')

    def get_finished_orders_list(self):
        """Выбрать только завершённые заказы."""
        statuses = (Order.DONE_STATUS, Order.CANCELED_STATUS, Order.CARD_CANCELED_UNPAID_STATUS)
        return self.filter(status__in = statuses).order_by('-pk')

    def get_unpaid_orders_list(self):
        """Выбрать только неоплаченные заказы."""
        statuses = (Order.NEW_STATUS, Order.AWAIT_PAYMENT_STATUS, Order.AWAIT_APPROVAL_STATUS,
            Order.CARD_AWAIT_PAYMENT_STATUS)
        return self.filter(status__in = statuses).order_by('-pk')


class Order(models.Model):
    CARD_PAY_DAYS = 2  # (карта) за сколько дней нужно оплатить заказ

    CANCELED_STATUS = 0
    NEW_STATUS = 1
    AWAIT_PAYMENT_STATUS = 2
    COMPLETING_STATUS = 3
    DELIVERING_STATUS = 4
    DONE_STATUS = 5
    CARD_AWAIT_PAYMENT_STATUS = 6
    PAID_AWAIT_COMPLETING_STATUS = 7
    AWAIT_APPROVAL_STATUS = 8
    CARD_CANCELED_UNPAID_STATUS = 9

    STATUS_CHOICES = (
        (CANCELED_STATUS, u'отменён'),
        (NEW_STATUS, u'новый'),
        (AWAIT_PAYMENT_STATUS, u'подтверждён, ожидает оплаты'),
        (AWAIT_APPROVAL_STATUS, u'ожидает проверки менеджером'),
        (CARD_AWAIT_PAYMENT_STATUS, u'готов к оплате картой'),
        (PAID_AWAIT_COMPLETING_STATUS, u'оплачен, ожидает комплектации'),
        (COMPLETING_STATUS, u'комплектуется'),
        (DELIVERING_STATUS, u'ожидает доставки'),
        (DONE_STATUS, u'выполнен'),
        (CARD_CANCELED_UNPAID_STATUS, u'отменён, не был оплачен в срок'),
    )

    # статусы заказов, оплачиваемых картой
    _CARD_STATUS_CHOICES = (
        (AWAIT_APPROVAL_STATUS, u'ожидает проверки менеджером'),
        (CARD_AWAIT_PAYMENT_STATUS, u'готов к оплате картой'),
        (PAID_AWAIT_COMPLETING_STATUS, u'оплачен, ожидает комплектации'),
        (COMPLETING_STATUS, u'комплектуется'),
        (DELIVERING_STATUS, u'ожидает доставки'),
        (DONE_STATUS, u'выполнен'),
        (CARD_CANCELED_UNPAID_STATUS, u'отменён, не был оплачен в срок'),
        (CANCELED_STATUS, u'отменён'),
    )

    # статусы заказов, оплачиваемых наличными
    _CASH_STATUS_CHOICES = (
        (NEW_STATUS, u'новый заказ'),
        (AWAIT_PAYMENT_STATUS, u'подтверждён, ожидает оплаты'),
        (COMPLETING_STATUS, u'комплектуется'),
        (DELIVERING_STATUS, u'ожидает доставки'),
        (DONE_STATUS, u'выполнен'),
        (CANCELED_STATUS, u'отменён'),
    )

    CARD_PAYMENT_METHOD = 0
    CASH_PAYMENT_METHOD = 1
    # по умолчанию, для админки
    PAYMENT_METHOD_CHOICES = (
        (CARD_PAYMENT_METHOD, u'картой'),
        (CASH_PAYMENT_METHOD, u'наличными'),
    )
    # для покупателей, на сайте
    _BUYER_PAYMENT_METHOD_CHOICES = (
        (CARD_PAYMENT_METHOD, u'Картой Visa или Mastercard на сайте'),
        (CASH_PAYMENT_METHOD, u'Безналичный расчёт по выставленному счёту'),
    )

    buyer = models.ForeignKey(Buyer, verbose_name=u'покупатель')

    last_name = models.CharField(u'Фамилия', max_length=30)
    first_name = models.CharField(u'Имя', max_length=30)
    mid_name = models.CharField(u'Отчество', max_length=30)

    city = models.CharField(u'город', max_length=50)
    address = models.CharField(u'адрес', max_length=100)
    phone = models.CharField(u'телефон', max_length=20)

    payment_method = models.PositiveSmallIntegerField(u'Способ оплаты', choices=PAYMENT_METHOD_CHOICES,
        default=CARD_PAYMENT_METHOD)

    sum = models.DecimalField(u"сумма заказа", max_digits=7, decimal_places=0, default=0)
    status = models.PositiveSmallIntegerField(u"статус", choices=STATUS_CHOICES, default=NEW_STATUS)

    cancel_date = models.DateTimeField(u'дата отмены', blank=True, null=True, default=None)
    cancel_reason = models.TextField(u'причина отмены', max_length=500, blank=True, default='')

    create_date = models.DateField(u'дата добавления', auto_now_add=True, blank=True, null=True)
    change_date = models.DateField(u'дата изменения', auto_now=True, blank=True, null=True)

    done_date = models.DateTimeField(u'дата выполнения', blank=True, null=True, default=None)

    pay_till = models.DateTimeField(u'оплатить до', blank=True, null=True, default=None)

    objects = OrderManager()

    class Meta:
        verbose_name = u"заказ"
        verbose_name_plural = u"заказы"

    def __unicode__(self):
        return u"%s: %s" % (self.get_full_fio(), self.sum,)

    def __init__(self, *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)

        # кешровать текущий статус заказа
        self._old_status = self.status if self.pk else None

        # добавить методы is_NAME_STATUS для проверки статуса
        status_name = [name for name in dir(Order) if name.endswith('_STATUS')]
        for name in status_name:
            setattr(self, 'is_%s' % name.lower(), curry(self._is_status, name))

    def save(self, *args, **kwargs):
        super(Order, self).save(*args, **kwargs)
        self._old_status = self.status if self.pk else None # кешировать текущий статус заказа

    def delete(self, *args, **kwargs):
        if self.is_paid() or self.orderpayment_set.count():
            raise Exception(u"You can't delete paid order!")
        super(Order, self).delete(*args, **kwargs)

    def _is_status(self, status_name):
        status = getattr(self, status_name.upper(), None)
        return self.status is status

    def get_status_choices(self):
        """Доступные статусы заказа, в зависимости от указанного способа оплаты."""
        if self.payment_method == self.CARD_PAYMENT_METHOD:
            return self._CARD_STATUS_CHOICES
        elif self.payment_method == self.CASH_PAYMENT_METHOD:
            return self._CASH_STATUS_CHOICES
        return None

    def _init_status(self):
        """Задать первый статус заказа в зависимости от выбранного способа оплаты.
            Вызывать исключительно для только что созданных заказов!
        """
        if self.status != self.NEW_STATUS:
            return

        if self.payment_method == self.CARD_PAYMENT_METHOD:
            self.status = self.AWAIT_APPROVAL_STATUS
        elif self.payment_method == self.CASH_PAYMENT_METHOD:
            self.status = self.NEW_STATUS # при оплате наличными, оставить статус по умолчанию

    def have_status_changed(self):
        return self._old_status != self.status

    def get_payment_method(self):
        """Наименование способа оплаты, для показа покупателю."""
        return dict(self._BUYER_PAYMENT_METHOD_CHOICES)[self.payment_method]

    def get_full_fio(self):
        """Полное ФИО."""
        return (u'%s %s %s' % (self.last_name, self.first_name, self.mid_name,)).strip()

    def list_shopping(self):
        res = []
        for item in self.items.all():
            res.append(u'%(count)d * %(name)s' % {'name': item.good.name, 'count': item.count})
        return mark_safe('<br/>'.join(res))

    list_shopping.short_description = u'Список покупок'
    list_shopping.allow_tags = True

    def get_ya_pay_form(self):
        """Возвращает платежную форму Яндекс-кассы для этого заказа."""
        try:
            user = User.objects.get(username=self.buyer.username)
        except:
            user = None
        payment, _ = Payment.objects.get_or_create(order_amount=self.sum,
                                                   payment_type=Payment.PAYMENT_TYPE.AC,
                                                   order_number=self.id,
                                                   )
        payment.customer_number=self.buyer.email
        payment.user=user
        payment.cps_email=self.buyer.email
        payment.cps_phone=self.buyer.phone
        payment.save()
        form = PaymentForm(instance=payment)
        return form

    def get_psbank_pay_form(self):
        """Возвращает платежную форму Промсвязьбанка для этого заказа."""
        def order_description():
            res = []
            for item in self.items.all():
                res.append(u'%s %s шт.' % (item.good.name.strip(), item.count,))
            return mark_safe(', '.join(res))
        backref = u'%s%s/' % (SHOP_SETTINGS['PSBANK_BACK_URL'], self.pk,)

        return psbank.get_pay_form(self.sum, u'RUB', self.pk, order_description(), backref)

    def is_psbank_payment(self):
        """Этот счёт оплачен через Промсвязьбанк?"""
        try:
            order_operation = get_list_or_404(OrderPayment.objects.order_by('-created_at'), order=self.pk,
                operation__trtype=psbank.PAY_TRTYPE, operation__result=psbank.SUCCESS_RESULT)[0]
            return True
        except Http404:
            return False

    def is_unpaid(self):
        """Этот счёт еще можно оплатить?
            Очень общий метод, показывает не оплачивался ли заказ вообще. Т.е. вернет True, даже если заказ находится
                на этапе проверки (хотя на данном этапе его оплатить еще нельзя).
            Если нужнен точный статус, то лучше его проверять явно.
        """
        return self.status in (self.NEW_STATUS, self.AWAIT_PAYMENT_STATUS, self.AWAIT_APPROVAL_STATUS,
            self.CARD_AWAIT_PAYMENT_STATUS)

    def is_paid(self):
        """Этот счёт оплачен?"""
        return self.status in (self.COMPLETING_STATUS, self.DELIVERING_STATUS, self.DONE_STATUS,
            self.PAID_AWAIT_COMPLETING_STATUS)

    def is_card_payment(self):
        return self.payment_method is self.CARD_PAYMENT_METHOD

    def is_cash_payment(self):
        return self.payment_method is self.CASH_PAYMENT_METHOD

    def is_done(self):
        return self.status is self.DONE_STATUS

    def is_canceled(self):
        return self.status in (self.CANCELED_STATUS, self.CARD_CANCELED_UNPAID_STATUS)

    def done(self, date=None):
        """Задать статус 'Выполнен'."""
        self.status = self.DONE_STATUS
        self.done_date = date or datetime.now()

    def cancel(self, reason=u'', date=None):
        """Отмена заказа."""
        self.status = self.CANCELED_STATUS
        self.cancel_reason = reason.strip()
        self.cancel_date = date or datetime.now()

    def card_cancel_unpaid(self, date=None):
        """(карта) Отмена заказа, неоплаченного в срок."""
        self.status = self.CARD_CANCELED_UNPAID_STATUS
        self.cancel_date = date or datetime.now()

    def set_pay_till(self):
        """(карта) Задать дату, до которой нужно оплатить заказ."""
        self.pay_till = datetime.now() + timedelta(days=self.CARD_PAY_DAYS)


class OrderedItem(models.Model):
    order = models.ForeignKey(Order, related_name="items")
    good = models.ForeignKey(Good, verbose_name=u'товар')
    price = models.DecimalField(u"цена", max_digits=7, decimal_places=0)
    count = models.PositiveIntegerField(u"количество")

    class Meta:
        verbose_name = u'товар'
        verbose_name_plural = u'товары'

    def __unicode__(self):
        return u'%s, %s руб, %s %s.' % (self.good, self.price, self.count, self.good.units)

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.good.price
        super(OrderedItem, self).save(*args, **kwargs)

    def sum(self):
        return self.price * self.count
    sum.short_description = u'Сумма'


class OrderPayment(models.Model):
    """Привязка заказов к операциям оплаты Промсвязьбанка."""
    order = models.ForeignKey(Order)
    operation = models.ForeignKey(psbank.Payment, verbose_name=u'Операция', related_name='+')
    created_at = models.DateTimeField(u'Дата проведения', auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)


class OrderNoReg(models.Model):
    """Заказ без регистрации."""

    CANCELED_STATUS = 0
    NEW_STATUS = 1
    AWAIT_PAYMENT_STATUS = 2
    COMPLETING_STATUS = 3
    DELIVERING_STATUS = 4
    DONE_STATUS = 5

    # статусы заказов
    STATUS_CHOICES = (
        (NEW_STATUS, u'новый заказ'),
        (AWAIT_PAYMENT_STATUS, u'подтверждён, ожидает оплаты'),
        (COMPLETING_STATUS, u'комплектуется'),
        (DELIVERING_STATUS, u'ожидает доставки'),
        (DONE_STATUS, u'выполнен'),
        (CANCELED_STATUS, u'отменён'),
    )

    name = models.CharField(u'имя', max_length=50)
    phone = models.CharField(u'телефон', max_length=30)

    sum = models.DecimalField(u'cумма заказа', max_digits=7, decimal_places=0, default=0)
    status = models.PositiveSmallIntegerField(u'статус', choices=STATUS_CHOICES, default=NEW_STATUS)

    create_date = models.DateField(u'дата добавления', auto_now_add=True, blank=True, null=True)
    change_date = models.DateField(u'дата изменения', auto_now=True, blank=True, null=True)

    cancel_date = models.DateTimeField(u'дата отмены', blank=True, null=True, default=None)
    done_date = models.DateTimeField(u'дата выполнения', blank=True, null=True, default=None)

    class Meta:
        verbose_name = u'заказ'
        verbose_name_plural = u'заказы без регистрации'

    def __unicode__(self):
        return u'%s: %s' % (self.name, self.sum,)

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        self.phone = self.phone.strip()
        super(OrderNoReg, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_paid():
            raise Exception(u"You can't delete paid order!")
        super(OrderNoReg, self).delete(*args, **kwargs)

    def is_paid(self):
        """Этот счёт оплачен?"""
        return self.status in (self.COMPLETING_STATUS, self.DELIVERING_STATUS, self.DONE_STATUS)

    def list_shopping(self):
        res = []
        for item in self.items.all():
            res.append(u'%(count)d * %(name)s' % {'name': item.good.name, 'count': item.count})
        return mark_safe('<br/>'.join(res))

    list_shopping.short_description = u'Список покупок'
    list_shopping.allow_tags = True

    def done(self, date=None):
        """Задать статус 'Выполнен'."""
        self.status = self.DONE_STATUS
        self.done_date = date or datetime.now()

    def cancel(self, date=None):
        """Отмена заказа."""
        self.status = self.CANCELED_STATUS
        self.cancel_date = date or datetime.now()


class OrderNoRegItem(models.Model):
    order = models.ForeignKey(OrderNoReg, related_name='items')
    good = models.ForeignKey(Good, verbose_name=u'товар')
    price = models.DecimalField(u'цена', max_digits=7, decimal_places=0)
    count = models.PositiveIntegerField(u'количество')

    class Meta:
        verbose_name = u'товар'
        verbose_name_plural = u'товары'

    def __unicode__(self):
        return u'%s, %s руб, %s %s.' % (self.good, self.price, self.count, self.good.units)

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.good.price
        super(OrderNoRegItem, self).save(*args, **kwargs)

    def sum(self):
        return self.price * self.count
    sum.short_description = u'Сумма'


class Sale(models.Model):
    sum = models.DecimalField(u"сумма заказа", max_digits=7, decimal_places=0)
    sale = models.DecimalField(u"процент скидки", max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = u"скидка на заказ"
        verbose_name_plural = u"скидки на заказы"

    def __unicode__(self):
        return u"%s: %s" % (self.sum, self.sale,)


class Discount(models.Model):
    sum = models.DecimalField(u"накопленная сумма", max_digits=7, decimal_places=0)
    sale = models.DecimalField(u"процент скидки", max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = u"накопительная скидка"
        verbose_name_plural = u"накопительные скидки"

    def __unicode__(self):
        return u"%s: %s" % (self.sum, self.sale,)


class ImportGoods(models.Model):
    """Импорт товаров."""
    NEW_STATUS = 0
    PROCESSING_STATUS = 1
    ERROR_STATUS = 2
    DONE_STATUS = 3
    DONE_WITH_ERRORS_STATUS = 4

    STATUS_CHOICES = (
        (NEW_STATUS, u'новый'),
        (PROCESSING_STATUS, u'выполняется'),
        (ERROR_STATUS, u'ошибка'),
        (DONE_STATUS, u'готово, без ошибок'),
        (DONE_WITH_ERRORS_STATUS, u'готово, есть ошибки'),
    )

    file = models.FileField(u'файл', upload_to='import/goods/')
    date = models.DateTimeField(u'дата добавления', auto_now_add=True)
    status = models.PositiveSmallIntegerField(u'статус', choices=STATUS_CHOICES, default=NEW_STATUS)
    log = models.TextField(u'лог', max_length=5000, default='', blank=True)

    class Meta:
        verbose_name = u'импорт товаров'
        verbose_name_plural = u'импорт товаров'

    def __unicode__(self):
        return u'%s' % self.date

    def save(self, *args, **kwargs):
        super(ImportGoods, self).save(*args, **kwargs)
        if self.status is self.NEW_STATUS:
            _import_goods_processing(self)


def _import_goods_processing(instance):
    """Импортирует товары."""
    _errors = False

    instance.status = ImportGoods.PROCESSING_STATUS
    instance.save()

    # индексы колонок в xls
    IDX_CHANGE = 0
    IDX_PRODUCER = 1
    IDX_NAME = 2
    IDX_ARTICUL = 3
    IDX_CATEGORY = 4
    IDX_DIMS = 5
    IDX_SALE = 6 # aka special
    IDX_NEW = 7
    IDX_DESCRIPTION = 8

    try:
        book = xlrd.open_workbook(instance.file.path)
        sh = book.sheet_by_index(0)
    except:
        instance.status = ImportGoods.ERROR_STATUS
        instance.log += u'Не удалось открыть файл: %s\n' % (instance.file.path,)
        instance.save()
        return

    # служебная рубрика "Новые товары"
    category_new_goods, category_new_goods_created = Category.objects.get_or_create(name=u'Новые товары',
        defaults={'hidden': True, 'never_available': True})

    # все существующие категории
    cache_categories = dict((x.pk, x) for x in Category.objects.all())

    missed_categories = set() # несуществующие категории

    dub_articuls = OrderedDict() # повторяющиеся артикулы

    random_articuls = [] # случайные артикулы, присвоенные товарам

    for rx in xrange(sh.nrows):
        row = sh.row(rx)

        good_name = row[IDX_NAME].value.strip()
        # если не задано название или это шапка таблицы, то пропустить строку
        if not good_name or good_name.lower() == u'наименование товара':
            continue

        try:
            good_articul = u'%d' % int(row[IDX_ARTICUL].value)
        except ValueError:
            good_articul = None

        good_change = (u'%s' % row[IDX_CHANGE].value).strip() == '+'
        good_producer = (u'%s' % row[IDX_PRODUCER].value).strip()
        good_dims = (u'%s' % row[IDX_DIMS].value).strip()
        good_sale = (u'%s' % row[IDX_SALE].value).strip() == '+'
        good_new = (u'%s' % row[IDX_NEW].value).strip() == '+'
        good_description = (u'%s' % row[IDX_DESCRIPTION].value).strip()

        try:
            _good_category_id = int(row[IDX_CATEGORY].value)
            good_category = cache_categories.get(_good_category_id)
            if not good_category:
                missed_categories.add(good_category) # запомнить категорию, как несуществующую
        except ValueError:
            good_category = None

        # товары, у которых есть артикул в xls
        if good_articul:
            try:
                # на сайте товар с таким артикулом уже есть
                good = Good.objects.get(articul=good_articul)
                good_created = False

                # включено "изменить" ?
                if good_change:
                    good.producer = good_producer
                    good.name = good_name
                    good.dims = good_dims
                    good.special = good_sale
                    good.new = good_new
                    good.description = good_description
                    if good_category:
                        good.category = good_category
                    good.save()

            except Good.DoesNotExist:
                # на сайте товара с таким артикулом нет
                good = Good(
                    articul = good_articul,
                    producer = good_producer,
                    name = good_name,
                    dims = good_dims,
                    special = good_sale,
                    new = good_new,
                    description = good_description
                )
                # если категория указана, то положить товар в неё, иначе положить в служебную категорию "Новые товары"
                good.category = good_category or category_new_goods
                good.save()
                good_created = True

            except Good.MultipleObjectsReturned:
                # на сайте несколько товаров с одним и тем же артикулом
                _errors = True
                dub_articuls[good_articul] = Good.objects.filter(articul=good_articul).values_list('pk', flat=True)
                continue # next good

        # товары, у которых нет артикула в xls
        else:
            good = Good(
                articul = 'S' + ''.join([choice('0123456789') for x in range(0, 6)]),
                producer = good_producer,
                name = good_name,
                dims = good_dims,
                special = good_sale,
                new = good_new,
                description = good_description
            )
            # если категория указана, то положить товар в неё, иначе положить в служебную категорию "Новые товары"
            good.category = good_category or category_new_goods
            good.save()
            good_created = True

            # запомнить товар и его новый случайный артикул
            random_articuls.append(tuple([good.articul, good.name, good.pk]))

    # записать в лог отсутствующие категории
    if missed_categories:
        instance.log += u'Не найдены категории: %s.\n' % ', '.join(['%s' % x for x in sorted(missed_categories)])

    # записать в лог случайные артикулы
    if random_articuls:
        instance.log += u'Товары без артикула. Артикул назначен сайтом:\n%s.\n' % ';\n'.join(
            '%s %s (%s)' % x for x in random_articuls)

    # записать в лог дублирующиеся артикулы
    if dub_articuls:
        instance.log += u'Повтор артикула:\n%s.\n' % '; '.join(
            '%s %s' % (k, sorted(v)) for k,v in dub_articuls.iteritems())

    if _errors:
        instance.status = ImportGoods.DONE_WITH_ERRORS_STATUS
    else:
        instance.status = ImportGoods.DONE_STATUS

    instance.save()

    update_category_counters()  # enable if Category.count_all is used on filters


class ImportPrices(models.Model):
    """Импорт цен."""

    def _make_upload_path(instance, filename):
        if instance.is_robot:
            return u'import/prices/robot/%s' % filename
        return u'import/prices/%s' % filename

    NEW_STATUS = 0
    PROCESSING_STATUS = 1
    ERROR_STATUS = 2
    DONE_STATUS = 3
    DONE_WITH_ERRORS_STATUS = 4

    STATUS_CHOICES = (
        (NEW_STATUS, u'новый'),
        (PROCESSING_STATUS, u'выполняется'),
        (ERROR_STATUS, u'ошибка'),
        (DONE_STATUS, u'готово, без ошибок'),
        (DONE_WITH_ERRORS_STATUS, u'готово, есть ошибки'),
    )

    file = models.FileField(u'файл', upload_to=_make_upload_path)
    date = models.DateTimeField(u'дата добавления', auto_now_add=True)
    status = models.PositiveSmallIntegerField(u'статус', choices=STATUS_CHOICES, default=NEW_STATUS)
    log = models.TextField(u'лог', max_length=5000, default='', blank=True)
    is_robot = models.BooleanField(u'робот', default=False, blank=True)

    class Meta:
        verbose_name = u'импорт цен'
        verbose_name_plural = u'импорт цен'

    def __unicode__(self):
        return u'%s' % self.date

    def save(self, *args, **kwargs):
        super(ImportPrices, self).save(*args, **kwargs)
        if self.status is self.NEW_STATUS:
            _import_prices_processing(self)


def _import_prices_processing(instance):
    """Импортирует цены."""
    _errors = False

    instance.status = ImportPrices.PROCESSING_STATUS
    instance.save()

    # индексы колонок в xls
    IDX_ARTICUL = 0
    IDX_PRICE = 1
    IDX_AVAILABLE = 2

    _t1 = time()

    try:
        book = xlrd.open_workbook(instance.file.path)
        sh = book.sheet_by_index(0)
    except:
        instance.status = ImportPrices.ERROR_STATUS
        instance.log += u'Не удалось открыть файл: %s\n' % (instance.file.path,)
        instance.save()
        return

    # кешировать артикулы всех товаров
    articuls_cache = Good.objects.values_list('articul', flat=True)

    def articul_exists(articul):
        return articul in articuls_cache

    missed_articuls = []
    processed_goods = []
    changed_goods = []
    unchanged_goods = []

    for rx in xrange(sh.nrows):
        row = sh.row(rx)

        try:
            good_articul = u'%d' % int(row[IDX_ARTICUL].value)
        except ValueError:
            good_articul = None

        try:
            good_price = int(row[IDX_PRICE].value)
        except ValueError:
            good_price = None

        # если не задан артикул или цена, то пропустить строку
        if not (good_articul and good_price):
            continue

        # если 0, 0.0 или пустота - товара нет в наличии, иначе есть
        good_available = True
        _available = row[IDX_AVAILABLE].value
        try:
            good_available = bool(int(float(_available)))
        except ValueError:
            try:
                good_available = bool(_available.strip())
            except AttributeError:
                _errors = True
                instance.log += (u'Товар %s. Ошибка в поле `Наличие`: %s. Значение по умолчанию: %s.\n' %
                    (good_articul, _available, good_available))
                instance.save()

        processed_goods.append(good_articul)

        try:
            # на сайте есть товар с таким артикулом
            if articul_exists(good_articul):
                good = Good.objects.get(articul=good_articul)
            else:
                raise Good.DoesNotExist

            # сохранить только если изменилась цена или флаг наличия
            if good.price != good_price or good.is_available != good_available:
                good.price = good_price
                good.is_available = good_available
                good.save()
                changed_goods.append(good_articul)
            else:
                unchanged_goods.append(good_articul)

        except Good.DoesNotExist:
            # на сайте товара с таким артикулом нет
            _errors = True
            missed_articuls.append(good_articul)
            continue

        except Good.MultipleObjectsReturned:
            # на сайте несколько товаров с одним и тем же артикулом
            _errors = True
            instance.log += u'Повтор в базе: %s.\n' % good_articul
            instance.save()
            continue

    _t2 = time()

    _max_items = 50

    # убрать дубли
    missed_articuls = uniquify_list(missed_articuls)
    changed_goods = uniquify_list(changed_goods)
    unchanged_goods = uniquify_list(unchanged_goods)

    # записать в лог отсутствующие на сайте артикулы
    if missed_articuls:
        _len = len(missed_articuls)
        instance.log += u'Товаров нет в каталоге: %s%s (всего %s)\n' % (', '.join(missed_articuls[:_max_items]),
            u', ...' if _len > _max_items else u'', _len)
        instance.save()

    # записать в лог неизменившиеся товары
    if unchanged_goods:
        _len = len(unchanged_goods)
        instance.log += u'Товары не изменились: %s%s (всего %s)\n' % (', '.join(unchanged_goods[:_max_items]),
            u', ...' if _len > _max_items else u'', _len)
        instance.save()

    # записать в лог прочую статистику
    instance.log += u'=== Обработано: %s\n' % len(set(processed_goods))
    instance.log += u'=== Изменилось: %s\n' % len(set(changed_goods))
    instance.log += u'=== Не изменилось: %s\n' % len(set(unchanged_goods))
    instance.log += u'=== Повторов в файле: %s\n' % (len(processed_goods) - len(set(processed_goods)))
    instance.log += u'=== Время: %.1f сек.\n' % abs(_t2 - _t1)

    if _errors:
        instance.status = ImportPrices.DONE_WITH_ERRORS_STATUS
    else:
        instance.status = ImportPrices.DONE_STATUS

    instance.save()

    update_category_counters()  # enable if Category.count_all is used on filters


class Available(models.Model):
    shop = models.ForeignKey(Shop)
    good = models.ForeignKey(Good)
    price = models.DecimalField(u"цена", max_digits=7, decimal_places=0)
    count = models.PositiveIntegerField(u"количество")
    sale = models.BooleanField(u'распродажа', default=False)

    class Meta:
        verbose_name = u"наличие в магазинах"
        verbose_name_plural = u"наличие в магазинах"


# TODO remove or rewrite to update Category counters
#def post_save_available_handler(sender, instance, created, **kwargs):
#    cats = instance.good.categories.all()
#    if instance.shop.online:
#        cats.update(count_online=F('count_online') + 1)
#        for item in cats:
#            item.save()
#
#post_save.connect(post_save_available_handler, sender=Available, dispatch_uid="shop.available")


# TODO remove or rewrite to update Category counters
#def pre_delete_available_handler(sender, instance, **kwargs):
#    cats = instance.good.categories.filter(count_online__gt=0) # чтобы не уводить счётчик в минус
#    if instance.shop.online:
#        cats.update(count_online=F('count_online') - 1)
#        for item in cats:
#            item.save()
#
#pre_delete.connect(pre_delete_available_handler, sender=Available, dispatch_uid="shop.available")


class PriceRequest(models.Model):
    STATUS_CHOICES = (
        ('N', u'Новый'),
        ('P', u'Обработан'),
    )

    phone = models.CharField(u'Телефон', max_length=20)
    email = models.EmailField(u'Электронная почта')
    subscribe = models.BooleanField(u'Присылать предложения', default=False, blank=True)

    good = models.ForeignKey('Good', verbose_name=u"товар")

    timestamp = models.DateTimeField(editable=False, verbose_name=u"запрос отправлен")
    status = models.CharField(max_length=1, default='N', choices=STATUS_CHOICES, verbose_name=u"статус")
    status_changed = models.DateTimeField(editable=False, null=True, blank=True, verbose_name=u"статус изменен")

    class Meta:
        verbose_name = u"запрос срока доставки"
        verbose_name_plural = u"запросы сроков доставки"

    def __unicode__(self):
        return u'Запрос на товар %s (%s)' % (
            self.good.__unicode__(),
            self.timestamp.strftime("%d.%m.%Y %H:%M"),
        )


class PhoneCallRequest(models.Model):
    STATUS_CHOICES = (
        ('N', u'Новый'),
        ('P', u'Обработан'),
    )

    phone = models.CharField(u'телефон', max_length=20)

    timestamp = models.DateTimeField(u'запрос отправлен', editable=False)
    status = models.CharField(u'статус', max_length=1, default='N', choices=STATUS_CHOICES)
    status_changed = models.DateTimeField(u'статус изменен', editable=False, null=True, blank=True)

    class Meta:
        verbose_name = u'запрос обратного звонка'
        verbose_name_plural = u'запросы обратного звонка'

    def __unicode__(self):
        return u'Запрос обратного звонка (%s)' % self.timestamp.strftime('%d.%m.%Y %H:%M')


def psbank_payment_received(sender, operation, **kwargs):
    """От Промсвязьбанка поступило сообщение об оплате."""
    if int(operation.result) != psbank.models.SUCCESS_RESULT: # только если `успешная оплата`
        return

    # обрабатывать только заказы со способом оплаты `картой` и статусом `готов к оплате картой` и неистекшим периодом
    order = get_object_or_404(
        Order,
        pk=int(operation.order),
        payment_method=Order.CARD_PAYMENT_METHOD,
        status=Order.CARD_AWAIT_PAYMENT_STATUS,
        pay_till__gte=datetime.now()
    )
    order.status = Order.PAID_AWAIT_COMPLETING_STATUS # изменить статус заказа на `Оплачен, ожидает комплектации`
    order.save()

    OrderPayment.objects.create(order=order, operation=operation) # сохранить связь заказа с операцией оплаты

    # отправить письмо менеджерам
    subject = SHOP_SETTINGS['ORDER_PAID_EMAIL_SUBJ']
    email_sender = SHOP_SETTINGS['EMAIL_SENDER']
    recipients = get_manager_emails()
    message = render_to_string('mail/order_paid.txt', {'order': order, 'oper': operation,})
    send_mail(subject, message, email_sender, recipients)

psbank.pay_received.connect(psbank_payment_received, sender=psbank.Payment, dispatch_uid='shop.psbank_payment_received')


# отображение статуса заказа на имя почтового шаблона
_ORDER_STATUS_TO_MSG_TEMPLATE_MAPPING = {
    Order.CANCELED_STATUS: mailing.ORDER_CANCELED_TEMPLATE,
    Order.NEW_STATUS: mailing.ORDER_NEW_TEMPLATE,
    Order.AWAIT_PAYMENT_STATUS: mailing.ORDER_AWAIT_PAYMENT_TEMPLATE,
    Order.COMPLETING_STATUS: mailing.ORDER_COMPLETING_TEMPLATE,
    Order.DELIVERING_STATUS: mailing.ORDER_DELIVERING_TEMPLATE,
    Order.DONE_STATUS: mailing.ORDER_DONE_TEMPLATE,
    # card
    Order.CARD_AWAIT_PAYMENT_STATUS: mailing.ORDER_CARD_AWAIT_PAYMENT_TEMPLATE,
    Order.PAID_AWAIT_COMPLETING_STATUS: mailing.ORDER_PAID_AWAIT_COMPLETING_TEMPLATE,
    Order.AWAIT_APPROVAL_STATUS: mailing.ORDER_AWAIT_APPROVAL_TEMPLATE,
    Order.CARD_CANCELED_UNPAID_STATUS: mailing.ORDER_CARD_CANCELED_UNPAID_TEMPLATE,
}


def order_status_changed(sender, instance, created, **kwargs):
    """Письмо покупателю при смене статуса заказа."""
    if instance.have_status_changed(): # отправить письмо, только если изменился статус заказа
        template = _ORDER_STATUS_TO_MSG_TEMPLATE_MAPPING.get(instance.status)
        if template:
            mailing.send_mail(template=template, buyer=instance.buyer, order=instance)
        else:
            mailing_logger.error(
                'shop.models.order_status_changed - Mapping not found for Order.status: %s.' % instance.status)

post_save.connect(order_status_changed, sender=Order, dispatch_uid='shop.order_status_changed')


def mail_no_buyer_profile(user, fail_silently=True):
    mail_admins(
        subject=u'no Buyer profile',
        message=u'User have no Buyer profile: %s, %s %s' % (user.email, user.username,
            u'(staff)' if user.is_staff or user.is_superuser else u''),
        fail_silently=fail_silently
    )


def get_manager_emails():
    return (Group.objects.get(id=SHOP_SETTINGS['EMAIL_GROUP'])
        .user_set.all().exclude(email='')
        .values_list('email', flat=True)
    )
