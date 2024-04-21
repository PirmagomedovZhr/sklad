# -*- coding: utf-8 -*-
from collections import defaultdict

from django.db import models
from django.contrib.auth.models import User

from mir_mebeli.shop.models import Order, Good, City


class Cart(models.Model):
    user = models.ForeignKey(User, related_name='carts', blank=True, null=True, default=None, unique=True)
    session = models.CharField(u'сессия', max_length=100, blank=True, default='', db_index=True)

    creation_date = models.DateTimeField(u'создана', auto_now_add=True)
    modification_date = models.DateTimeField(u'изменена', auto_now_add=True)

    # прочие данные (будут нужны для оформления заказа)

    last_name = models.CharField(u'фамилия', max_length=30, blank=True, default='')
    first_name = models.CharField(u'имя', max_length=30, blank=True, default='')
    mid_name = models.CharField(u'отчество', max_length=30, blank=True, default='')

    city = models.ForeignKey(City, verbose_name=u'город', blank=True, null=True, default=None)

    address = models.CharField(u'адрес', max_length=100, blank=True, default='')
    phone = models.CharField(u'телефон', max_length=20, blank=True, default='')

    payment_method = models.PositiveSmallIntegerField(u'способ оплаты', choices=Order.PAYMENT_METHOD_CHOICES,
        blank=True, null=True, default=Order.CARD_PAYMENT_METHOD)

    class Meta:
        verbose_name = u'корзина'
        verbose_name_plural = u'корзины'
        ordering = ('-creation_date',)

    def __unicode__(self):
        return u'%s, %s' % (self.user, self.session)

    def add(self, product, quantity=1):
        """Если товар уже в корзине, увеличивает его кол-во.
            Если товара в корзине нет, то добавляет его.
            Возвращает созданую/измененную запись.
        """
        quantity = int(quantity)
        cart_item = self.get_item(product)
        if not cart_item:
            cart_item = CartItem.objects.create(
                cart=self,
                product=product,
                quantity=max(quantity, 1),  # make sure it never goes lower than 1
                price=product.price
            )
        elif cart_item and cart_item.quantity + quantity > 0:
            cart_item.quantity += quantity
            cart_item.save()
        return cart_item

    def update(self, product, quantity):
        """Изменяет товар в корзине.
            Возвращает измененный товар.
        """
        quantity = int(quantity)
        cart_item = self.get_item(product)
        if cart_item and quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        return cart_item

    def merge_duplicates(self):
        """Если в корзине было создано несколько записей для одного и того же товара -
            собрать их в одну запись."""
        cart_items = self.get_items().order_by().order_by('product', '-quantity')

        products = defaultdict(list)
        for x in cart_items:
            products[x.product.pk].append(x)

        # no duplicates?
        if len(products) == len(cart_items):
            return

        for prod, prod_items in products.items():
            cart_item = prod_items[0]
            cart_item.quantity = sum([x.quantity for x in prod_items])
            cart_item.save()
            if len(prod_items) > 1:
                [x.delete() for x in prod_items[1:]]

    def get_item(self, product):
        """Возвращает товар из корзины."""
        try:
            return CartItem.objects.select_related().filter(cart=self, product=product).order_by('-quantity')[0]
        except IndexError:
            return None

    def get_items(self):
        """Возвращает товары в корзине."""
        return CartItem.objects.select_related().filter(cart=self).order_by('-pk')

    def get_items_count(self):
        """Возвращает кол-во товаров в корзине."""
        return CartItem.objects.filter(cart=self).count()

    def get_zero_price_items_count(self):
        """Возвращает кол-во товаров с ценой 0 в корзине."""
        return CartItem.objects.filter(cart=self, price=0).count()

    #

    def get_payment_method(self):
        """Наименование способа оплаты, для показа покупателю."""
        return dict(Order._BUYER_PAYMENT_METHOD_CHOICES)[self.payment_method]

    def is_card_payment(self):
        """Оплата карточкой?"""
        return self.payment_method is Order.CARD_PAYMENT_METHOD

    def is_cash_payment(self):
        """Оплата наличкой?"""
        return self.payment_method is Order.CASH_PAYMENT_METHOD

    def get_full_fio(self):
        """Полное ФИО."""
        return (u'%s %s %s' % (self.last_name, self.first_name, self.mid_name,)).strip()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, verbose_name=u'корзина')
    product = models.ForeignKey(Good, verbose_name=u'товар')
    quantity = models.PositiveIntegerField(u'кол-во')
    price = models.DecimalField(u'цена', max_digits=7, decimal_places=0, default=0)

    class Meta:
        verbose_name = u'товар'
        verbose_name_plural = u'товары'
        ordering = ('cart',)

    def __unicode__(self):
        return u'%s, %s шт., %s руб.' % (self.product, self.quantity, self.price)

    def total_price(self):
        return int(self.quantity * self.price)


def update_cart_after_login(request, old_cart=None):
    """Обновить корзину текущего покупателя после его логина.

        old_cart - объект модели Cart анонимного пользователя, которого только что залогинили

        1. если у анонима не было корзины - ничего не делать
        2. если у анонима была корзина, а у юзера корзины еще нет - привязать корзину анонима к юзеру
        3. если у анонима была корзина и у юзера есть корзина - добавить товары из корзины анонима в корзину юзера
    """
    if not old_cart:
        return

    try:
        user_cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        old_cart.user = request.user
        old_cart.save()
    else:
        for old_cart_item in old_cart.get_items():
            user_cart.add(old_cart_item.product, old_cart_item.quantity)
        old_cart.delete()
