# -*- coding: utf-8 -*-
import datetime
from decimal import Decimal

from django.contrib import admin
from django.contrib.admin.filterspecs import RelatedFilterSpec, FilterSpec
from django.utils.encoding import smart_unicode, force_unicode
from django.core.mail import send_mail
from django.conf import settings

from model_link_admin_widget import ModelLinkAdminFields
from mir_mebeli.shop.models import (Category, Good, Shop, Buyer, City, Order, OrderedItem,
    OrderNoReg, OrderNoRegItem, PriceRequest, PhoneCallRequest, ImportGoods, ImportPrices)
from .good_types import GOOD_TYPES, GOOD_FIELDS
# from mir_mebeli.shop.models import Color, Sale, Available, Discount
from mir_mebeli.shop.forms import OrderAdminForm, OrderedItemAdminForm, CategoryAdminForm, GoodAdminForm

import psbank


SHOP_SETTINGS = getattr(settings, 'SHOP_SETTINGS')


class CategoryFilterSpec(RelatedFilterSpec):
    def __init__(self, *args, **kwargs):
        super(CategoryFilterSpec, self).__init__(*args, **kwargs)
        all_cats = []
        for cat in Category.objects.filter(level=0).order_by('order', 'name'):
            all_cats.append(cat)
            for subcat in cat.get_descendants().order_by('lft'):
                all_cats.append(subcat)
        self.lookup_choices = [(cat.pk, u'%s %s' % ('-' * cat.level, smart_unicode(cat.name),)) for cat in all_cats]

    def title(self):
        return self.lookup_title

FilterSpec.filter_specs.insert(0, (lambda f: bool(f.rel and hasattr(f, 'category_filter_spec')), CategoryFilterSpec))


class CategoryNoLeafNodesFilterSpec(RelatedFilterSpec):
    def __init__(self, *args, **kwargs):
        super(CategoryNoLeafNodesFilterSpec, self).__init__(*args, **kwargs)
        all_cats = []
        for cat in Category.objects.filter(level=0).order_by('order', 'name'):
            all_cats.append(cat)
            for subcat in cat.get_descendants().order_by('lft'):
                all_cats.append(subcat)
        all_cats = [x for x in all_cats if not x.is_leaf_node()] # убрать ноды, у которых нет потомков
        self.lookup_choices = [(cat.pk, u'%s %s' % ('-' * cat.level, smart_unicode(cat.name),)) for cat in all_cats]

    def title(self):
        return self.lookup_title

FilterSpec.filter_specs.insert(0,
    (lambda f: bool(f.rel and hasattr(f, 'category_no_leaf_nodes_filter_spec')), CategoryNoLeafNodesFilterSpec))


class GoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'articul', 'producer', 'category', 'is_available', 'special', 'new',)
    list_filter = ['is_available', 'category', 'date']
    search_fields = ('=pk', 'name', 'display_name', 'articul', 'producer')
    ordering = ['-id']
    form = GoodAdminForm

    class Media:
        css = {'all': ('css/shop-good-custom-admin.css',)}

    def get_form(self, request, obj=None, **kwargs):
        # убрать из формы поля, которые не относятся к выбранному типу товара
        if obj and obj.category_id and obj.category.good_type:
            try:
                exclude = set()
                fields = GOOD_TYPES[obj.category.good_type]['fields']
                for key in GOOD_FIELDS:
                    if key not in fields:
                        exclude.add(key)
                self.exclude = exclude
            except KeyError:
                pass
        return super(GoodAdmin, self).get_form(request, obj, **kwargs)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'pk', 'name', 'category_path', 'good_type', 'name_in_xls',)
    list_display_links = ('pk', 'name', 'name_in_xls',)
    list_editable = ('order',)
    list_filter = ('basic', 'never_available', 'hidden', 'parent',)
    readonly_fields = ('count_all', 'count_online', 'pk',)
    search_fields = ('=pk', 'name', 'name_in_xls',)
    form = CategoryAdminForm

    def __init__(self,*args,**kwargs):
        super(CategoryAdmin, self).__init__(*args, **kwargs)
        from django.contrib.admin.views import main
        main.EMPTY_CHANGELIST_VALUE = '-'

    def category_path(self, obj):
        return u' >> ' .join(cat.name for cat in obj.get_ancestors())
    category_path.short_description = u'Путь категории'


class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_in_xls', 'address', 'region', 'display', 'online',)


# class SaleAdmin(admin.ModelAdmin):
#     list_display = ('sum', 'sale',)


# class DiscountAdmin(admin.ModelAdmin):
#     list_display = ('sum', 'sale',)


# class AvailableAdmin(admin.ModelAdmin):
#     list_display = ('shop', 'good', 'price', 'sale',)


class OrderedItemInline(admin.TabularInline):
    model = OrderedItem
    form = OrderedItemAdminForm
    fields = ('good', 'price', 'count', 'sum',)
    readonly_fields = ('price', 'sum',)
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'sum', 'create_date', 'change_date', 'status', 'payment_method', 'list_shopping',)
    list_filter = ('create_date', 'change_date', 'payment_method', 'status',)
    search_fields = ('=pk', 'last_name', 'first_name', 'mid_name', 'city', 'address', 'phone', '=sum',)
    fields = ('last_name', 'first_name', 'mid_name', 'city', 'address', 'phone', 'buyer', 'payment_method',
        'status', 'done_date', 'cancel_date', 'cancel_reason', 'pay_till', 'order_payment_info', 'sum')
    readonly_fields = ('order_payment_info', 'sum',)
    form = OrderAdminForm
    list_per_page = 50
    inlines = (OrderedItemInline,)

    def order_payment_info(self, obj):
        from yandex_money.models import Payment

        op = obj.orderpayment_set.all()
        if op:
            return op[0].operation.created_at.strftime('%d.%m.%Y %H:%M')

        op = Payment.objects.filter(order_number=obj.id)
        if op and op[0].is_payed:
                return op[0].performed_datetime.strftime('%d.%m.%Y %H:%M')

        return u'не поступал'

    order_payment_info.short_description = u'Банковский платёж'

    def save_model(self, request, obj, form, change):
        status = form.cleaned_data.get('status')
        if status == Order.DONE_STATUS and obj.done_date is None:
            obj.done()
        elif status == Order.CANCELED_STATUS and obj.cancel_date is None:
            obj.cancel()
        elif status == Order.CARD_CANCELED_UNPAID_STATUS and obj.cancel_date is None:
            obj.card_cancel_unpaid()
        elif status == Order.CARD_AWAIT_PAYMENT_STATUS and obj.pay_till is None:
            obj.set_pay_till()
        super(OrderAdmin, self).save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue='../%s/'):
        self.after_saving_model_and_inlines(obj)
        return super(OrderAdmin, self).response_add(request, obj)

    def response_change(self, request, obj):
        self.after_saving_model_and_inlines(obj)
        return super(OrderAdmin, self).response_change(request, obj)

    def after_saving_model_and_inlines(self, obj):
        if obj.status == Order.DONE_STATUS:
            return
        _sum = Decimal(0)
        for item in obj.items.all():
            _sum += item.sum()
        if obj.sum != _sum:
            obj.sum = _sum
            obj.save()

    def get_actions(self, request):
        """Убрать из списка групповых действий возможность удаления заказа."""
        actions = super(OrderAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        """Нельзя удалить оплаченный заказ."""
        if obj and (obj.is_paid() or obj.orderpayment_set.count()):
            return False
        return True

    def log_change(self, request, object, message):
        """Записать в лог доп.информацию при изменении заказа.
            Перегрузка метода ModelAdmin.log_change
        """
        message = u'%s Статус: %s.' % (message, object.get_status_display())

        from django.contrib.contenttypes.models import ContentType
        from django.contrib.admin.models import LogEntry, CHANGE

        LogEntry.objects.log_action(
            user_id         = request.user.pk,
            content_type_id = ContentType.objects.get_for_model(object).pk,
            object_id       = object.pk,
            object_repr     = force_unicode(object),
            action_flag     = CHANGE,
            change_message  = message
        )


class OrderNoRegInline(admin.TabularInline):
    model = OrderNoRegItem
    form = OrderedItemAdminForm
    fields = ('good', 'price', 'count', 'sum',)
    readonly_fields = ('price', 'sum',)
    extra = 0


class OrderNoRegAdmin(admin.ModelAdmin):
    list_display = ('name', 'sum', 'create_date', 'change_date', 'status', 'list_shopping',)
    list_filter = ('create_date', 'change_date', 'status',)
    search_fields = ('=pk', 'name', 'phone', '=sum',)
    fields = ('name', 'phone', 'status', 'done_date', 'cancel_date', 'sum')
    readonly_fields = ('sum',)
    list_per_page = 50
    inlines = (OrderNoRegInline,)

    def save_model(self, request, obj, form, change):
        status = form.cleaned_data.get('status')
        if status == Order.DONE_STATUS and obj.done_date is None:
            obj.done()
        elif status == Order.CANCELED_STATUS and obj.cancel_date is None:
            obj.cancel()
        super(OrderNoRegAdmin, self).save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue='../%s/'):
        self.after_saving_model_and_inlines(obj)
        return super(OrderNoRegAdmin, self).response_add(request, obj)

    def response_change(self, request, obj):
        self.after_saving_model_and_inlines(obj)
        return super(OrderNoRegAdmin, self).response_change(request, obj)

    def after_saving_model_and_inlines(self, obj):
        if obj.status == Order.DONE_STATUS:
            return
        _sum = Decimal(0)
        for item in obj.items.all():
            _sum += item.sum()
        if obj.sum != _sum:
            obj.sum = _sum
            obj.save()

    def get_actions(self, request):
        """Убрать из списка групповых действий возможность удаления заказа."""
        actions = super(OrderNoRegAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        """Нельзя удалить оплаченный заказ."""
        if obj and obj.is_paid():
            return False
        return True

    def log_change(self, request, object, message):
        """Записать в лог доп.информацию при изменении заказа.
            Перегрузка метода ModelAdmin.log_change
        """
        message = u'%s Статус: %s.' % (message, object.get_status_display())

        from django.contrib.contenttypes.models import ContentType
        from django.contrib.admin.models import LogEntry, CHANGE

        LogEntry.objects.log_action(
            user_id         = request.user.pk,
            content_type_id = ContentType.objects.get_for_model(object).pk,
            object_id       = object.pk,
            object_repr     = force_unicode(object),
            action_flag     = CHANGE,
            change_message  = message
        )


class PriceRequestAdmin(ModelLinkAdminFields, admin.ModelAdmin):
    list_display = ('good', 'format_timestamp', 'phone', 'email', 'subscribe', 'status',)
    list_filter = ('timestamp', 'status', 'subscribe',)
    modellink = ('good',)
    search_fields = ('=pk', '=good__pk', 'phone', 'email', 'good__name',)

    class Media:
        js = ('js/shop-custom-admin.js',)

    def format_timestamp(self, obj):
        return obj.timestamp.strftime('%d.%m.%Y %H:%M')

    format_timestamp.short_description = 'Date'

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('status', 'N') == 'P' and obj.status_changed is None:
            obj.status_changed = datetime.datetime.now()
            period = obj.status_changed - obj.timestamp
            subject = u'Запрос цены обработан менеджером'
            sender =  SHOP_SETTINGS['EMAIL_SENDER']
            recipients = SHOP_SETTINGS['CHIEF_EMAILS']
            message = u'Запрос на товар %s поступил %s; обработан %s; время выполнения: %d часов, %d минут; менеджер: %s.' % (
                obj.good,
                obj.timestamp.strftime('%d.%m.%Y %H:%M'),
                obj.status_changed.strftime('%d.%m.%Y %H:%M'),
                period.days * 24 + period.seconds / 60 / 60,
                period.seconds / 60 % 60,
                request.user,
            )
            send_mail(subject, message, sender, recipients) # TODO обернуть в try/except
        super(PriceRequestAdmin, self).save_model(request, obj, form, change)


class PhoneCallRequestAdmin(admin.ModelAdmin):
    list_display = ('format_timestamp', 'phone', 'status',)
    list_filter = ('timestamp', 'status',)
    search_fields = ('=pk', 'phone',)

    class Media:
        js = ('js/shop-custom-admin.js',)

    def format_timestamp(self, obj):
        return obj.timestamp.strftime('%d.%m.%Y %H:%M')

    format_timestamp.short_description = 'Date'

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('status', 'N') == 'P' and obj.status_changed is None:
            obj.status_changed = datetime.datetime.now()
            period = obj.status_changed - obj.timestamp
            subject = u'Запрос обратного звонка обработан менеджером'
            sender =  SHOP_SETTINGS['EMAIL_SENDER']
            recipients = SHOP_SETTINGS['CHIEF_EMAILS']
            message = u'Запрос обратного звонка поступил %s; обработан %s; время выполнения: %d часов, %d минут; менеджер: %s.' % (
                obj.timestamp.strftime('%d.%m.%Y %H:%M'),
                obj.status_changed.strftime('%d.%m.%Y %H:%M'),
                period.days * 24 + period.seconds / 60 / 60,
                period.seconds / 60 % 60,
                request.user,
            )
            send_mail(subject, message, sender, recipients) # TODO обернуть в try/except
        super(PhoneCallRequestAdmin, self).save_model(request, obj, form, change)


class CityAdmin(admin.ModelAdmin):
    list_display = ('ordering', 'name',)
    list_display_links = ('name',)
    list_editable = ('ordering',)


class ImportGoodsAdmin(admin.ModelAdmin):
    list_display = ('date', 'file', 'status',)
    list_filter = ('status',)
    readonly_fields = ('date', 'status',)


class ImportPricesAdmin(admin.ModelAdmin):
    list_display = ('date', 'file', 'status', 'is_robot',)
    list_filter = ('status', 'is_robot',)
    readonly_fields = ('date', 'status', 'is_robot',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Good, GoodAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(Buyer)
admin.site.register(City, CityAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderNoReg, OrderNoRegAdmin)
admin.site.register(PriceRequest, PriceRequestAdmin)
admin.site.register(PhoneCallRequest, PhoneCallRequestAdmin)
admin.site.register(ImportGoods, ImportGoodsAdmin)
admin.site.register(ImportPrices, ImportPricesAdmin)

# admin.site.register(Color)
# admin.site.register(Sale, SaleAdmin)
# admin.site.register(Discount, DiscountAdmin)
# admin.site.register(Available, AvailableAdmin)
