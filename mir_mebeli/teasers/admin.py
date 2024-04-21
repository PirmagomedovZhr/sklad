# -*- coding: utf-8 -*-
from django.contrib import admin

from mir_mebeli.teasers.models import Teaser


class TeaserAdmin(admin.ModelAdmin):
    list_display = ['name', 'published', 'new', 'image', 'link']
    list_editable = ['published', 'new']
    list_filter = ['published', 'new']


admin.site.register(Teaser, TeaserAdmin)
