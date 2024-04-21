# -*- coding: utf-8 -*-

from cms.app_base import CMSApp
from menu import NewsMenu
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _

class CMSPluginNewsApphook(CMSApp):
    name = u"Новости"
    urls = ["cmsplugin_news.urls"]
    menu = [NewsMenu]


apphook_pool.register(CMSPluginNewsApphook)    
