# -*- coding: utf-8 -*-

from mir_mebeli.guestbook.models import *
# from travel_easy.appart.forms import ItemForm
from django.contrib import admin

class MessageAdmin(admin.ModelAdmin):
    list_display = ('fio', 'email', 'created')

admin.site.register(Message, MessageAdmin)
