# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from menu import ShopMenu
# from menu import CategoryMenu


# class CategoryApphook(CMSApp):
#     name = _("Categories")
#     # ССЫЛКИ ТЕПЕРЬ В mir_mebeli.urls
# #    urls = ["shop.categories.urls"] # отключил, чтобы ссылки каталога начинались с корня.
#     urls = []
# #    menu = [CategoryMenu]
#     # отключил меню каталога - много товаров, очень тормозит
#     menu = []


class ShopApphook(CMSApp):
    name = _("Shops")
    urls = ["shop.shops.urls"]
    menu = [ShopMenu]


# apphook_pool.register(CategoryApphook)
apphook_pool.register(ShopApphook)
