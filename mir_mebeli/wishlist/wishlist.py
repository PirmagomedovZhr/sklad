# -*- coding: utf-8 -*-
from utils import wishlist_required, WishlistItemDoesNotExist
import models


class Wishlist:
    """Обертка над моделью вишлиста и его товарами.
        Вишлист в БД создается только при добавлении первого товара.
    """
    wishlist = None  # вишлист текущего покупателя. None - если его еще нет

    def __init__(self, request, create=False):
        if create:
            self.wishlist = self._get_or_create_wishlist(request)  # force wishlist creation
        else:
            self.wishlist = self._get_wishlist_db(request)

    def _get_or_create_wishlist(self, request):
        """Возвращает вишлист текущего покупателя. Если вишлиста еще нет, то создает ее."""
        wishlist = self._get_wishlist_db(request)
        if not wishlist:
            wishlist = self._create_wishlist_db(request)

        return wishlist

    def _get_wishlist_db(self, request):
        """Возвращает вишлист текущего покупателя. Если вишлиста у него еще нет, то возвращает None."""
        if request.user.is_authenticated():
            try:
                return models.Wishlist.objects.get(user=request.user)
            except models.Wishlist.DoesNotExist:
                return None
        else:
            try:
                return models.Wishlist.objects.get(session=request.session.session_key)
            except models.Wishlist.DoesNotExist:
                return None

    def _create_wishlist_db(self, request):
        """Создает вишлист для текущей сессии и/или покупателя."""
        if request.session.session_key is None:
            request.session.save()

        wishlist = models.Wishlist(session=request.session.session_key)
        if request.user.is_authenticated():
            wishlist.user = request.user

        wishlist.save()
        return wishlist

    # операции с вишлистом
    # если вишлиста у текущего покупателя еще нет - выбрасывают исключение WishlistDoesNotExist

    @wishlist_required
    def add_product(self, product):
        """Добавляет товар в вишлист или изменяет его."""
        return self.wishlist.add(product)

    @wishlist_required
    def remove_product(self, product):
        """Удаляет товар из вишлиста."""
        item = self.wishlist.get_item(product=product)
        if item:
            item.delete()

    # возвращают информацию по вишлисту
    # если вишлиста у текущего покупателя еще нет - исключение не выбрасывают

    def is_empty(self):
        """Возвращет True, если в вишлисте нет товаров. Если вишлиста еще нет - тоже возвращает True."""
        if self.wishlist:
            return self.wishlist.get_items_count() == 0
        return True

    def items_count(self):
        """Возвращает кол-во товаров в вишлисте. Если вишлиста еще нет - возвращает 0."""
        if self.wishlist:
            return self.wishlist.get_items_count()
        return 0
