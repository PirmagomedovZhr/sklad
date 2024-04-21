# -*- coding: utf-8 -*-
from django.contrib import admin

from models import Wishlist, WishlistItem


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    fields = ['product']
    readonly_fields = fields
    extra = 1
    can_delete = False


class WishlistAdmin(admin.ModelAdmin):
    inlines = [WishlistItemInline]
    list_display = ['user', 'created_at', 'updated_at']
    search_fields = ['user__email']

    def get_readonly_fields(self, request, obj=None):
        """Make all fields readonly."""
        return list(set(
            [field.name for field in self.opts.local_fields] +
            [field.name for field in self.opts.local_many_to_many]
        ))


admin.site.register(Wishlist, WishlistAdmin)
