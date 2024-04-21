# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template

from cms.sitemaps import CMSSitemap


def sitemap(request):
    extra_context = {
        'cms_sitemap': CMSSitemap(),
    }
    return direct_to_template(request, 'cms/pages/sitemap.html', extra_context)
