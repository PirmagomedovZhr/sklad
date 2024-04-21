# -*- coding: utf-8 -*-
from django.contrib import admin

from models import MessageTemplate, Message


class MessageAdmin(admin.ModelAdmin):
    list_display = ['subject', 'to', 'format_created_at', 'sent', 'attempts']
    list_display_links = ['subject']
    list_filter = ['sent', 'created_at']
    date_hierarchy = 'created_at'
    search_fields = ['=order__pk', 'to', 'subject']

    def format_created_at(self, obj):
        return obj.created_at.strftime('%d.%m.%Y %H:%M:%S')
    format_created_at.short_description = u'Дата'
    format_created_at.admin_order_field = 'created_at'


class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ['subject', 'template']


admin.site.register(Message, MessageAdmin)
admin.site.register(MessageTemplate, MessageTemplateAdmin)
