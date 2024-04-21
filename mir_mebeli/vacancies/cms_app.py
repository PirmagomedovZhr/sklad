# -*- coding: utf-8 -*-

from cms.app_base import CMSApp
from menu import VacancyMenu
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _

class VacanciesApphook(CMSApp):
    name = u"Вакансии"
    urls = ["vacancies.urls"]
    menu = [VacancyMenu]

apphook_pool.register(VacanciesApphook)    
