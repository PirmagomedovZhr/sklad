# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from menus.base import Menu, NavigationNode
from menus.menu_pool import menu_pool
from cms.menu_bases import CMSAttachMenu

from mir_mebeli.shop.models import Shop


class ShopMenu(CMSAttachMenu):
    name = _("Shops")

    def get_nodes(self, request):
        nodes = []

        for shop in Shop.objects.all().order_by('lft'):
            nnode = NavigationNode(
                shop.name,
                shop.get_absolute_url(),
                'shop-%d' % shop.pk
            )
            nodes.append(nnode)

        return nodes


menu_pool.register_menu(ShopMenu)
