# -*- coding: utf-8 -*-
from django.contrib import admin
from django.db import models

from readonly_fileinput_widget import ReadonlyFileInput
from models import Message, Recipients


class MessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'created_at']
    readonly_fields = ['name', 'email', 'phone', 'body']
    fields = ['name', 'email', 'phone', 'body', 'file1', 'file2', 'file3', 'file4']

    formfield_overrides = {
        models.FileField: {'widget': ReadonlyFileInput},
    }

    def has_add_permission(self, request):
        return False

admin.site.register(Message, MessageAdmin)
admin.site.register(Recipients)
