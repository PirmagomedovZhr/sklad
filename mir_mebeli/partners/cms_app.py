# -*- coding: utf-8 -*-
from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool


class PartnersApphook(CMSApp):
    name = u'Partners'
    urls = ['partners.urls']


apphook_pool.register(PartnersApphook)
