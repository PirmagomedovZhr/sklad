# -*- coding: utf-8 -*-
from django.contrib import admin

from models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    fields = ('product', 'quantity', 'price')
    readonly_fields = fields
    extra = 1
    can_delete = False


class CartAdmin(admin.ModelAdmin):
    inlines = (CartItemInline,)
    list_display = ('user', 'creation_date', 'modification_date')
    search_fields = ['user__email']

    def get_readonly_fields(self, request, obj=None):
        return list(set(
            [field.name for field in self.opts.local_fields] +
            [field.name for field in self.opts.local_many_to_many]
        ))


admin.site.register(Cart, CartAdmin)
