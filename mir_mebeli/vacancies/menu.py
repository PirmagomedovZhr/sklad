from menus.base import Menu, NavigationNode
from models import Vacancy
from django.core.urlresolvers import NoReverseMatch
from menus.menu_pool import menu_pool
from cms.app_base import CMSApp
from django.utils.translation import ugettext_lazy as _
from cms.menu_bases import CMSAttachMenu

class VacancyMenu(CMSAttachMenu):

    name = _("Vacancy")

    def get_nodes(self, request):
        import logging
        nodes = []

        for vacancy in Vacancy.objects.all().order_by('lft'):
            nodes.append(NavigationNode(vacancy.__unicode__(), vacancy.get_absolute_url(), 'vacancy-%d' % vacancy.pk, None))
        return nodes


menu_pool.register_menu(VacancyMenu)