# -*- coding: utf-8 -*-
from collections import namedtuple

from shop.models import Buyer
from shop.global_discount import get_conf as get_global_discount_conf

from .utils import cart_required
from . import models


GlobalDiscount = namedtuple('GlobalDiscount', ['price', 'percent', 'discount'])


class Cart(object):
    """Обертка над моделью корзины и ее товарами.
        Корзина в БД создается только при добавлении первого товара.
    """
    buyer = None
    cart = None  # корзина текущего покупателя. None - если ее еще нет

    def __init__(self, request, create=False):
        if create:
            self.cart = self._get_or_create_cart(request)  # force cart creation
        else:
            self.cart = self._get_cart_db(request)

        # сохранить ссылку на профиль покупателя (для внутреннего использования)
        if request.user.is_authenticated():
            try:
                self.buyer = request.user.buyer
            except Buyer.DoesNotExist:
                pass

        self.global_discount_conf = get_global_discount_conf()

    def _get_or_create_cart(self, request):
        """Возвращает корзину текущего покупателя. Если корзины еще нет, то создает ее."""
        cart = self._get_cart_db(request)
        if not cart:
            cart = self._create_cart_db(request)

        return cart

    def _get_cart_db(self, request):
        """Возвращает корзину текущего покупателя. Если корзины у него еще нет, то возвращает None."""
        if request.user.is_authenticated():
            try:
                return models.Cart.objects.get(user=request.user)
            except models.Cart.DoesNotExist:
                return None
        else:
            try:
                return models.Cart.objects.filter(session=request.session.session_key, user=None).order_by(
                    '-creation_date', '-modification_date', '-pk')[0]
            except IndexError:
                return None

    def _create_cart_db(self, request):
        """Создает корзину для текущей сессии и/или покупателя."""
        if request.session.session_key is None:
            request.session.save()

        cart = models.Cart(session=request.session.session_key)
        if request.user.is_authenticated():
            cart.user = request.user

        cart.save()
        return cart

    # операции с корзиной
    # если корзины у текущего покупателя еще нет - выбрасывают исключение CartDoesNotExist

    @cart_required
    def add_product(self, product, quantity=1):
        """Добавляет товар в корзину или изменяет его."""
        return self.cart.add(product, quantity)

    @cart_required
    def update_product(self, product, quantity):
        """Изменяет товар в корзине."""
        return self.cart.update(product, quantity)

    @cart_required
    def remove_product(self, product):
        """Удаляет товар из корзины."""
        item = self.cart.get_item(product=product)
        if item:
            item.delete()

    # возвращают информацию по корзине
    # если корзины у текущего покупателя еще нет - исключение не выбрасывают

    def cached_get_goods_dict(self):
        """Возвращает словарь всех товаров в корзине. Ключ - id товара.
            Если корзины еще нет - возвращает пустой словарь.
            Данные кешируются.
        """
        if self.cart:
            if not hasattr(self, '_cached_goods'):
                self._cached_goods = dict((x.product_id, x) for x in self.cart.get_items())
            return self._cached_goods
        return dict()

    def cached_get_good(self, good_id):
        """Возвращает товар по его id.
            Если товара нет в корзине или если нет корзины - возвращает None.
            Данные кешируются.
        """
        return self.cached_get_goods_dict().get(good_id)

    def is_empty(self):
        """Возвращет True, если в корзине нет товаров. Если корзины еще нет - тоже возвращает True."""
        if self.cart:
            return self.cart.get_items_count() == 0
        return True

    def cached_is_empty(self):
        """Кешированная версия метода is_empty."""
        if self.cart:
            if not hasattr(self, '_cached_is_empty'):
                self._cached_is_empty = self.cached_items_count() == 0
            return self._cached_is_empty
        return True

    def items_count(self):
        """Возвращает кол-во товаров в корзине. Если корзины еще нет - возвращает 0."""
        return self.cart.get_items_count() if self.cart else 0

    def cached_items_count(self):
        """Кешированная версия метода items_count."""
        if self.cart:
            if not hasattr(self, '_cached_items_count'):
                self._cached_items_count = self.items_count()
            return self._cached_items_count
        return 0

    def zero_price_items_count(self):
        """Возвращает кол-во товаров с ценой 0 в корзине. Если корзины еще нет - возвращает 0."""
        if self.cart:
            return self.cart.get_zero_price_items_count()
        return 0

    def cost(self):
        """Возвращает общую стоимость товаров в корзине, но без стоимости доставки.
            Если корзины еще нет - возвращает 0.
        """
        if self.cart:
            total_price = 0
            for item in self.cart.get_items():
                total_price += item.total_price()
            return total_price
        return 0

    def cached_cost(self):
        """Кешированная версия метода cost."""
        if self.cart:
            if not hasattr(self, '_cached_cost'):
                total_price = 0
                for item in self.cached_get_goods_dict().itervalues():
                    total_price += item.total_price()
                self._cached_cost = total_price
            return self._cached_cost
        return 0

    def total_price(self):
        """Возвращает общую стоимость товаров в корзине.
            Если корзины еще нет - возвращает 0.
        """
        if self.cart:
            return self.cost()
        return 0

    def cached_total_price(self):
        """Кешированная версия метода total_price."""
        return self.cached_cost()

    def _global_discount_percent(self, price):
        """Вычисляет процент скидки на базе переданной стоимости."""
        _settings = self.global_discount_conf
        curr_p = (0, 0)
        for p in _settings['PERCENTS']:
            if price >= p[0] and p[0] > curr_p[0]:
                curr_p = p
        return curr_p[1]

    def global_discount(self):
        """Возвращает namedtuple типа GlobalDiscount.
            Из расчета базы исключаются товары из категорий, которым скидка не положена.
            Если общие скидки отключены или период прошел - возвращает 0.
            Результат кешируется внутри объекта.
        """
        _zero = GlobalDiscount(0, 0, 0)

        try:
            return getattr(self, '_cache_global_discount')
        except AttributeError:
            self._cache_global_discount = _zero

        _settings = self.global_discount_conf
        if _settings['ENABLED'] and not _settings['EXPIRED']:
            _price = 0

            if self.cart:
                for item in self.cart.get_items():
                    _item_price = item.total_price()
                    if _item_price > 0:
                        item_category_id = item.product.category_id
                        # отбросить товары из указанных категорий
                        if item_category_id not in _settings['EXCLUDE_CATEGORY_IDS']:
                            _price += _item_price

            if _price:
                _percent = self._global_discount_percent(_price)
                self._cache_global_discount = GlobalDiscount(
                    price = _price,
                    percent = _percent,
                    discount = int(_price * _percent / 100)
                )

        return self._cache_global_discount

    def cost_with_global_discount(self):
        """Возвращает общую стоимость товаров в корзине с учетом общей скидки, но без стоимости доставки.
        """
        return self.cost() - self.global_discount().discount

    def total_price_with_global_discount(self):
        """Возвращает общую стоимость товаров в корзине с учетом общей скидки плюс стоимость доставки.
        """
        return self.total_price() - self.global_discount().discount
