# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

from mir_mebeli.shop.models import Good


class Wishlist(models.Model):
    user = models.ForeignKey(User, related_name='wishlists', blank=True, null=True, default=None, unique=True)
    session = models.CharField(u'сессия', max_length=100, blank=True, default='', db_index=True)

    created_at = models.DateTimeField(u'создано', auto_now_add=True)
    updated_at = models.DateTimeField(u'изменено', auto_now=True)

    class Meta:
        verbose_name = u'вишлист'
        verbose_name_plural = u'вишлисты'
        ordering = ['-created_at']

    def __unicode__(self):
        return u'%s, %s' % (self.user or u'аноним', self.session)

    def add(self, product):
        """Добавить товар в вишлист, если его еще там нет.
            Возвращает созданую/полученную запись.
        """
        obj, created = WishlistItem.objects.get_or_create(wishlist=self, product=product)
        return obj

    def remove(self, product):
        """Удаляет товар из вишлиста."""
        WishlistItem.objects.filter(wishlist=self, product=product).delete()

    def get_item(self, product):
        """Возвращает товар из вишлиста."""
        try:
            return WishlistItem.objects.select_related().filter(wishlist=self, product=product)[0]
        except IndexError:
            return None

    def get_items(self):
        """Возвращает товары в вишлисте."""
        return WishlistItem.objects.select_related().filter(wishlist=self).order_by('-created_at')

    def get_items_count(self):
        """Возвращает кол-во товаров в вишлисте."""
        return WishlistItem.objects.filter(wishlist=self).count()


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, verbose_name=u'вишлист')
    product = models.ForeignKey(Good, verbose_name=u'товар')

    created_at = models.DateTimeField(u'создано', auto_now_add=True)

    class Meta:
        verbose_name = u'товар'
        verbose_name_plural = u'товары'
        ordering = ['-created_at']

    def __unicode__(self):
        return u'%s' % self.product


def update_wishlist_after_login(request, old_wishlist=None):
    """Обновить вишлист текущего покупателя после его логина.

        old_wishlist - объект модели Wishlist анонимного пользователя, которого только что залогинили

        1. если у анонима не было вишлиста - ничего не делать
        2. если у анонима был вишлист, а у юзера вишлиста еще нет - привязать вишлист анонима к юзеру
        3. если у анонима был вишлист и у юзера есть вишлист - добавить товары из вишлиста анонима в вишлист юзера
    """
    if not old_wishlist:
        return

    try:
        user_wishlist = Wishlist.objects.get(user=request.user)
    except Wishlist.DoesNotExist:
        old_wishlist.user = request.user
        old_wishlist.save()
    else:
        for old_wishlist_item in old_wishlist.get_items():
            user_wishlist.add(old_wishlist_item.product)
        old_wishlist.delete()
