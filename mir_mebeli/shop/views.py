# -*- coding: utf-8 -*-
import datetime
from collections import defaultdict
from StringIO import StringIO
import traceback

import xlwt

from django.views.decorators.cache import never_cache
from django.template import RequestContext, loader
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, Http404
from django.core.mail import send_mail, mail_admins
from django.core.urlresolvers import reverse
from django.contrib import auth
from django.shortcuts import get_object_or_404, get_list_or_404, redirect, render_to_response
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import simplejson as json
from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.views.decorators import staff_member_required
from django.middleware.common import _is_internal_request
from django.conf import settings

from mir_mebeli.cart import Cart, update_cart_after_login
from mir_mebeli.wishlist.wishlist import Wishlist
from mir_mebeli.wishlist.models import update_wishlist_after_login
from mir_mebeli.wishlist.views import _get_wishlist_dict
from mir_mebeli.shop.models import (Good, Buyer, PriceRequest, Order, OrderedItem, OrderPayment, PhoneCallRequest,
    mail_no_buyer_profile, get_manager_emails, OrderNoReg, OrderNoRegItem)
from mir_mebeli.shop.forms import (DivErrorList, SearchForm, ReqPriceForm, ProfileForm, ChangePasswordForm,
    RegistrationForm, LoginForm, ResetPasswordForm, OrderCheckoutForm, OrderConfirmForm, ReqPhoneCallForm,
    OrderCancelForm, OrderNoRegForm)

from mir_mebeli import psbank, mailing
from mir_mebeli.utilities import safe_int


SHOP_SETTINGS = getattr(settings, 'SHOP_SETTINGS')
PASSWORD_MIN_LEN = getattr(settings, 'PASSWORD_MIN_LEN ', 7)
KUHNI_NA_ZAKAZ_CATEGORY_ID = getattr(settings, 'KUHNI_NA_ZAKAZ_CATEGORY_ID ', None)


def _get_cart_dict(request, cart=None):
    if not cart:
        cart = Cart(request)

    data = {
        'items_count': cart.items_count(),
        'price': cart.cost(),
        'total_price': cart.total_price(),
        'total_discount': cart.global_discount().discount,
        'total_discount_percent': cart.global_discount().percent,
    }

    if request.user.is_authenticated():
        try:
            buyer = request.user.buyer
            data['unpaid_orders_count'] = buyer.order_set.get_unpaid_orders_list().count(),
        except Buyer.DoesNotExist:
            pass

    return data


def cart_add_product(request, product_id=None, quantity=1):
    """Добавить товар в корзину."""
    quantity = int(quantity)
    if quantity < 1:
        raise Exception('Wrong product quantity.')

    product = get_object_or_404(Good, pk=product_id)

    cart = Cart(request, create=True) # force cart creation
    cart_item = cart.add_product(product, quantity)

    if request.is_ajax():
        data = _get_cart_dict(request, cart)
        data['item_qty'] = cart_item.quantity
        data['item_total_price'] = cart_item.total_price()
        return HttpResponse(json.dumps(data), mimetype='application/json')

    try:
        return redirect(request.META['HTTP_REFERER'])
    except KeyError:
        return redirect('cart')


def cart_remove_product(request, product_id=None):
    """Удалить товар из корзины."""
    product = get_object_or_404(Good, pk=product_id)

    cart = Cart(request, create=True) # force cart creation
    cart.remove_product(product)

    if request.is_ajax():
        data = _get_cart_dict(request, cart)
        return HttpResponse(json.dumps(data), mimetype='application/json')

    try:
        return redirect(request.META['HTTP_REFERER'])
    except KeyError:
        return redirect('cart')


def cart_set_product_quantity(request, product_id, quantity):
    """Изменить кол-во товара в корзине.
        Если товара в корзине нет - добавить его.
    """
    quantity = int(quantity)
    if quantity < 1:
        raise Exception('Wrong product quantity.')

    product = get_object_or_404(Good, pk=product_id)

    cart = Cart(request, create=True) # force cart creation
    cart_item = cart.update_product(product, quantity)
    if not cart_item:
        cart_item = cart.add_product(product, quantity)

    if request.is_ajax():
        data = _get_cart_dict(request, cart)
        data['item_qty'] = cart_item.quantity
        data['item_total_price'] = cart_item.total_price()
        return HttpResponse(json.dumps(data), mimetype='application/json')
    else:
        return redirect('cart')


def cart_inc_or_dec_product_quantity(request, product_id, mode):
    """Увеличить/уменьшить на 1 кол-во товара в корзине."""
    if mode not in ('inc', 'dec'):
        raise Http404

    quantity = 1
    if mode == 'dec':
        quantity = -1

    product = get_object_or_404(Good, pk=product_id)

    cart = Cart(request, create=True) # force cart creation
    cart_item = cart.add_product(product, quantity)

    if request.is_ajax():
        data = _get_cart_dict(request, cart)
        data['item_qty'] = cart_item.quantity
        data['item_total_price'] = cart_item.total_price()
        return HttpResponse(json.dumps(data), mimetype='application/json')
    else:
        return redirect('cart')


def get_cart(request):
    """Корзина."""
    cart = Cart(request)
    cart_obj = cart.cart

    extra_context = {'cart': cart}
    extra_context.update(_get_wishlist_dict(request))

    if request.is_ajax():
        data = _get_cart_dict(request, cart)
        return HttpResponse(json.dumps(data), mimetype='application/json')

    if request.user.is_authenticated():
        try:
            buyer = request.user.buyer
            initial = {
                'last_name': buyer.last_name,
                'first_name': buyer.first_name,
                'mid_name': buyer.mid_name,
                'city': buyer.city.pk if buyer.city else None,
                'address': buyer.address,
                'phone': buyer.phone,
                'subscribe': buyer.subscribe,
                'email': request.user.email,
            }
            extra_context['profile_form'] = ProfileForm(user=request.user, initial=initial)
        except Buyer.DoesNotExist:
            pass

        extra_context['change_password_form'] = ChangePasswordForm(user=request.user)
        extra_context['order_cancel_form'] = OrderCancelForm()
    else:
        extra_context['order_noreg_form'] = OrderNoRegForm()

    if cart_obj:
        cart_obj.merge_duplicates()

    # достать реферер для ссылки "Назад"
    extra_context['back_url'] = None
    referer = request.META.get('HTTP_REFERER', None)
    if referer:
        domain = request.get_host()
        if reverse('cart') not in referer and _is_internal_request(domain, referer):
            extra_context['back_url'] = referer

    return direct_to_template(request, 'cms/pages/cart.html', extra_context)


# def apply_filter(request, state=None):
#     request.session['filter'] = state == 'enable'
#     referer = request.META.get('HTTP_REFERER', None)
#     return HttpResponseRedirect(referer)


@never_cache
def logout(request):
    auth.logout(request)
    redirect_to = request.REQUEST.get('next', '/')
    return redirect(redirect_to)


def req_price(request, good_id=None):
    """Запрос срока доставки товара."""
    form_class = ReqPriceForm

    if request.POST:
        form = form_class(request.POST, error_class=DivErrorList)
        if form.is_valid():
            good = Good.objects.get(pk=good_id)

            price_request = PriceRequest.objects.create(
                phone = form.cleaned_data.get('phone', ''),
                email = form.cleaned_data.get('email', ''),
                subscribe = form.cleaned_data.get('subscribe', False),
                good = good,
                timestamp = datetime.datetime.now()
            )

            category = good.category
            if category:
                subject = u'Запрос срока доставки товара с сайта sklad51.ru'
                sender = SHOP_SETTINGS['EMAIL_SENDER']
                message = render_to_string('mail/req_price.txt', {'price_request': price_request,})

                if not category.email:
                    recipients = SHOP_SETTINGS['FALLBACK_EMAILS']
                    subject += u'. Рубрика "%s": email не заполнен.' % category
                else:
                    recipients = (category.email,)

                # письмо менеджеру
                send_mail(subject, message, sender, recipients)

                # письмо покупателю, если рубрика "Кухни на заказ"
                if KUHNI_NA_ZAKAZ_CATEGORY_ID and category.pk == KUHNI_NA_ZAKAZ_CATEGORY_ID:
                    # TODO изменить тему и текст письма
                    send_mail(u'Письмо покупателю',
                        render_to_string('mail/req_price_user.txt', {'price_request': price_request,}),
                        SHOP_SETTINGS['EMAIL_SENDER'], price_request.email
                    )
    else:
        form = form_class(error_class=DivErrorList)

    return HttpResponse(render_to_string('ajax/form-response.html', {'form': form,},
        context_instance=RequestContext(request)), mimetype="application/json")


@require_POST
@csrf_protect
def req_phone_call(request):
    """Запрос обратного звонка."""
    if not request.is_ajax():
        return HttpResponseBadRequest()

    form = ReqPhoneCallForm(request.POST)
    if form.is_valid():
        phone_call_request = PhoneCallRequest.objects.create(
            phone = form.cleaned_data['phone'],
            timestamp = datetime.datetime.now()
        )

        subject = u'Запрос обратного звонка с сайта sklad51.ru'
        sender =  SHOP_SETTINGS['EMAIL_SENDER']
        recipients = get_manager_emails()
        message = render_to_string('mail/req_phone_call.txt', {'phone_call_request': phone_call_request,})

        send_mail(subject, message, sender, recipients) # TODO обернуть в try/except

    data = {
        'success': form.is_valid(),
        'field_errors': form.errors,
        'form_errors': form.non_field_errors(),
        'message': u'Ваша заявка принята!' if form.is_valid() else u'',
    }
    return HttpResponse(json.dumps(data), mimetype='application/json')


def send_order_mail(order):
    recipients = get_manager_emails()
    subject = u'Заказ от покупателя на сайте sklad51.ru'
    sender = SHOP_SETTINGS['EMAIL_SENDER']
    message = render_to_string('mail/order.txt', {'order': order})
    return send_mail(subject, message, sender, recipients)


def send_order_noreg_mail(order):
    recipients = get_manager_emails()
    subject = u'Заказ без регистрации на сайте sklad51.ru'
    sender = SHOP_SETTINGS['EMAIL_SENDER']
    message = render_to_string('mail/order_noreg.txt', {'order': order})
    return send_mail(subject, message, sender, recipients)


#def show_psbank_payment_info(request, order_id):
#    """Показать клиенту информацию об оплаченном заказе."""
#    template_name = 'cms/pages/psbank_payment_info.html'
#    fail_url = '/korzina/'
#    if not request.user.is_authenticated():
#        return redirect(fail_url)
#    try:
#        order = get_object_or_404(Order, pk=order_id, buyer=request.user)
#        order_operation = get_list_or_404(OrderPayment.objects.order_by('-created_at'), order=order_id,
#            operation__trtype=psbank.PAY_TRTYPE, operation__result=psbank.SUCCESS_RESULT)[0]
#        dictionary = {'order': order, 'oper': order_operation.operation,}
#        return render_to_response(template_name, dictionary, context_instance=RequestContext(request))
#    except Http404:
#        return redirect(fail_url)


@login_required
@require_POST
@csrf_protect
def profile_edit(request):
    """Редактирование реквизитов покупателя."""
    if not request.is_ajax():
        return HttpResponseBadRequest()

    form = ProfileForm(user=request.user, data=request.POST)
    if form.is_valid():
        cleaned_data = form.cleaned_data

        buyer = request.user.buyer
        buyer.mid_name = cleaned_data['mid_name']
        buyer.phone = cleaned_data['phone']
        buyer.city = cleaned_data['city']
        buyer.address = cleaned_data['address']
        buyer.subscribe = cleaned_data['subscribe']
        buyer.save()

        request.user.email = cleaned_data['email']
        request.user.last_name = cleaned_data['last_name']
        request.user.first_name = cleaned_data['first_name']
        request.user.save()

    data = {
        'success': form.is_valid(),
        'field_errors': form.errors,
        'form_errors': form.non_field_errors(),
        'message': u'Данные сохранены.' if form.is_valid() else u'',
    }
    return HttpResponse(json.dumps(data), mimetype='application/json')


@login_required
@require_POST
@csrf_protect
def change_password(request):
    """Изменение пароля."""
    if not request.is_ajax():
        return HttpResponseBadRequest()

    form = ChangePasswordForm(user=request.user, data=request.POST)
    if form.is_valid():
        new_password = form.cleaned_data['password1']
        request.user.set_password(new_password)
        request.user.save()

    data = {
        'success': form.is_valid(),
        'field_errors': form.errors,
        'form_errors': form.non_field_errors(),
        'message': u'Пароль изменён.' if form.is_valid() else u'',
    }
    return HttpResponse(json.dumps(data), mimetype='application/json')


@csrf_protect
@never_cache
def register_and_login(request):
    """Регистрация, вход и сброс пароля покупателя."""
    login_form_class = LoginForm
    login_form_prefix = 'login'
    register_form_class = RegistrationForm
    register_form_prefix = 'register'
    reset_form_class = ResetPasswordForm
    reset_form_prefix = 'reset'

    redirect_to = request.REQUEST.get('next', '/')

    extra_context = {
        'login_form': login_form_class(prefix=login_form_prefix),
        'register_form': register_form_class(prefix=register_form_prefix),
        'reset_form': reset_form_class(prefix=reset_form_prefix),
        'next': redirect_to,
        'cart': Cart(request),
    }

    if request.method == 'POST':
        form = None
        ajax_success_msg = u''

        if 'login' in request.POST:
            extra_context['login_form'] = form = login_form_class(data=request.POST, prefix=login_form_prefix)
            if form.is_valid():
                _login_user(request, form.get_user())
                ajax_success_msg = u'Успешный вход в магазин.'

        elif 'register' in request.POST:
            extra_context['register_form'] = form = register_form_class(data=request.POST, prefix=register_form_prefix)
            if form.is_valid():
                new_user = register_buyer(
                    request,
                    form.cleaned_data.get('email', ''),
                    form.cleaned_data.get('password1')
                )
                # send_registration_mail(new_user) # now send with mailing app
                ajax_success_msg = u'Успешная регистрация.'

        elif 'reset' in request.POST:
            extra_context['reset_form'] = form = reset_form_class(data=request.POST, prefix=reset_form_prefix)
            redirect_to = None
            if form.is_valid():
                buyer = form.get_user()
                new_password = Buyer.objects.make_random_password(length=PASSWORD_MIN_LEN)
                buyer.set_password(new_password)
                buyer.save()

                email = form.cleaned_data.get('email')
                if buyer.email == email:
                    send_new_password_mail(buyer, new_password)
                    ajax_success_msg = u'Пароль отправлен Вам по электронной почте.'

        if form:
            if form.is_valid() and not request.is_ajax():
                return redirect(redirect_to)
            elif request.is_ajax():
                data = {
                    'success': form.is_valid(),
                    'field_errors': form.errors,
                    'form_errors': form.non_field_errors(),
                    'message': ajax_success_msg if form.is_valid() else u'',
                    'redirect': redirect_to if form.is_valid() else None,
                }
                return HttpResponse(json.dumps(data), mimetype='application/json')

    return direct_to_template(request, 'cms/pages/auth/register_and_login.html', extra_context)


def _login_user(request, user):
    """Залогинить пользователя и при необходимости перетащить корзину."""
    cart = Cart(request)
    cart_obj = cart.cart

    wishlist = Wishlist(request)
    wishlist_obj = wishlist.wishlist

    auth.login(request, user)

    if cart_obj:
        update_cart_after_login(request, cart_obj)  # перетащить анонимную корзину

    if wishlist_obj:
        update_wishlist_after_login(request, wishlist_obj)  # перетащить анонимный вишлист


def register_buyer(request, email, password):
    """Зарегистрировать нового покупателя, после чего залогинить его."""
    buyer = Buyer.objects.create_buyer(email, password)
    user = auth.authenticate(username=buyer.username, password=password)
    _login_user(request, user)
    mailing.send_mail(template=mailing.REG_THANKS_TEMPLATE, buyer=buyer, password=password)
    return user


# def send_registration_mail(user):
#     """Отправить сообщение об успешной регистрации."""
#     recipients = (user.email,)
#     subject = u'Регистрация на сайте sklad51.ru'
#     sender = SHOP_SETTINGS['EMAIL_SENDER']
#     message = render_to_string('mail/registration.txt', {'user': user})
#     return send_mail(subject, message, sender, recipients)


def send_new_password_mail(buyer, new_password):
    """Отправить новый пароль покупателю на почту."""
    recipients = (buyer.email,)
    subject = u'Восстановление пароля на сайте sklad51.ru'
    sender = SHOP_SETTINGS['EMAIL_SENDER']
    message = render_to_string('mail/new_password.txt', {
        'buyer': buyer,
        'new_password': new_password,
    })
    return send_mail(subject, message, sender, recipients)


@login_required
@csrf_protect
def order_checkout(request):
    """Оформить заказ."""
    cart = Cart(request)
    if cart.is_empty():
        return redirect('cart')

    form_class = OrderCheckoutForm

    try:
        buyer = request.user.buyer
    except Buyer.DoesNotExist:
        mail_no_buyer_profile(request.user)
        return redirect('error_no_buyer_profile')

    cart_obj = cart.cart

    if request.method == 'POST':
        form = form_class(data=request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # сохранить данные заказа в корзину
            cart_obj.last_name = data['last_name']
            cart_obj.first_name = data['first_name']
            cart_obj.mid_name = data['mid_name']
            cart_obj.city = data['city']
            cart_obj.address = data['address']
            cart_obj.phone = data['phone']
            cart_obj.payment_method = data['payment_method']
            cart_obj.save()

            # перейти к подтверждению заказа только если указан город
            if cart_obj.city:
                return redirect('shop-order-confirm')
    else:
        def _city():
            if cart_obj.city: return cart_obj.city.pk
            if buyer.city: return buyer.city.pk
            return None

        initial = {
            'last_name': cart_obj.last_name or buyer.last_name,
            'first_name': cart_obj.first_name or buyer.first_name,
            'mid_name': cart_obj.mid_name or buyer.mid_name,
            'city': _city(),
            'address': cart_obj.address or buyer.address,
            'phone': cart_obj.phone or buyer.phone,
            'payment_method': cart_obj.payment_method or Order.CARD_PAYMENT_METHOD,
        }
        form = form_class(initial=initial)

    return direct_to_template(request, 'cms/pages/order_checkout.html', {'form': form, 'cart': cart,})


@login_required
@csrf_protect
def order_confirm(request):
    """Подтвердить заказ."""
    cart = Cart(request)
    if cart.is_empty():
        return redirect('cart')

    cart_obj = cart.cart

    # вернуться к оформлению заказа, если не указан город
    if not cart_obj.city:
        return redirect('shop-order-checkout')

    form_class = OrderConfirmForm

    try:
        buyer = request.user.buyer
    except Buyer.DoesNotExist:
        mail_no_buyer_profile(request.user)
        return redirect('error_no_buyer_profile')

    if request.method == 'POST':
        form = form_class(data=request.POST)
        if form.is_valid():
            # сохранить реквизиты покупателя в профиль
            buyer.last_name = cart_obj.last_name
            buyer.first_name = cart_obj.first_name
            buyer.mid_name = cart_obj.mid_name
            buyer.address = cart_obj.address
            buyer.phone = cart_obj.phone
            if cart_obj.city:
                buyer.city = cart_obj.city
            buyer.save()

            # создаём заказ
            order = Order(
                buyer = buyer,
                last_name = cart_obj.last_name,
                first_name = cart_obj.first_name,
                mid_name = cart_obj.mid_name,
                city = cart_obj.city.name,
                address = cart_obj.address,
                phone = cart_obj.phone,
                payment_method = cart_obj.payment_method,
                sum = cart.cost_with_global_discount(),  # учесть общую скидку, если она есть
            )

            order._init_status() # задать статус заказа

            order.save()

            # скопировать покупки из корзины в заказ
            for cart_item in cart_obj.get_items():
                if cart_item.quantity < 1:
                    continue

                OrderedItem.objects.create(
                    order = order,
                    good = cart_item.product,
                    price = cart_item.price,
                    count = cart_item.quantity
                )

            send_order_mail(order) # отправить e-mail сообщение группе менеджеров

            cart_obj.delete() # удалить корзину

            if order.is_card_payment():
                return redirect('shop-order-go-bank', order.pk)
            else:
                return redirect('shop-order-done', order.pk)
    else:
        initial = {
            'last_name': buyer.last_name,
            'first_name': buyer.first_name,
            'mid_name': buyer.mid_name,
            'address': buyer.address,
            'phone': buyer.phone,
            'payment_method': Order.CARD_PAYMENT_METHOD,
        }
        form = form_class(initial=initial)

    return direct_to_template(request, 'cms/pages/order_confirm.html', {'form': form, 'cart': cart,})


@login_required
@csrf_protect
def order_go_bank(request, order_id):
    """При оплате картой - страница для перехода на сайт банка."""
    order = get_object_or_404(Order, pk=order_id, buyer=request.user)
    if order.is_card_payment() and order.status == Order.CARD_AWAIT_PAYMENT_STATUS:
        return direct_to_template(request, 'cms/pages/order_go_bank.html', {'order': order})
    else:
        return redirect('shop-order-done', order.pk)


@login_required
@csrf_protect
def order_done(request, order_id):
    """Результат заказа."""
    order = get_object_or_404(Order, pk=order_id, buyer=request.user)
    return direct_to_template(request, 'cms/pages/order_done.html', {'order': order,})


@login_required
@csrf_protect
def order_cancel(request, order_id):
    """Отмена заказа. Но только если он еще не был оплачен."""
    redirect_to = reverse('cart')

    if request.method == 'POST' and '_cancel' in request.POST:
        return redirect(redirect_to)

    order = get_object_or_404(Order, pk=order_id, buyer=request.user)

    if order.is_paid():
        raise Http404

    form_class = OrderCancelForm
    extra_context = {
        'order': order,
        'order_cancel_form': form_class(),
    }

    if request.method == 'POST':
        extra_context['order_cancel_form'] = form = form_class(data=request.POST)
#        ajax_success_msg = u'Заказ №%s отменён.' % order.pk

        if form.is_valid():
            order.cancel(form.cleaned_data['reason'])
            order.save()

        if form.is_valid() and not request.is_ajax():
            return redirect(redirect_to)
        elif request.is_ajax():
            data = {
                'success': form.is_valid(),
                'field_errors': form.errors,
                'form_errors': form.non_field_errors(),
#                'message': ajax_success_msg if form.is_valid() else u'',
#                'redirect': redirect_to if form.is_valid() else None,
                'cart': _get_cart_dict(request),
            }
            return HttpResponse(json.dumps(data), mimetype='application/json')

    return direct_to_template(request, 'cms/pages/order_cancel.html', extra_context)


@login_required
def success_payment(request):
    """Информация о заказе при удачной оплате."""
    from yandex_money.models import Payment

    cd = request.GET
    order_id = cd.get('orderNumber')
    payment = Payment.objects.get(order_number=order_id)
    message = None
    if payment.is_payed:
        order = get_object_or_404(Order, id=order_id)
        order.status = Order.PAID_AWAIT_COMPLETING_STATUS
        message = u'Поздравляем! Ваш заказ оплачен.'
        order.save()

    return direct_to_template(request, 'cms/pages/order_info.html', {'order': order, 'message': message})


@login_required
def fail_payment(request):
    """Информация о заказе."""
    cd = request.GET
    order_id = cd.get('orderNumber')
    order = get_object_or_404(Order, id=order_id)
    message = u'При оплате возникли проблемы.'
    return direct_to_template(request, 'cms/pages/order_info.html', {'order': order, 'message': message})


@login_required
def order_info(request, order_id):
    """Информация о заказе."""
    order = get_object_or_404(Order, pk=order_id, buyer=request.user)
    return direct_to_template(request, 'cms/pages/order_info.html', {'order': order})


@require_POST
@csrf_protect
def order_noreg(request):
    """Оформить заказ без регистрации."""
    if not request.is_ajax():
        return HttpResponseBadRequest('ajax only')

    if request.user.is_authenticated():
        return HttpResponseBadRequest('only for unauthenticated users')

    cart = Cart(request)
    cart_obj = cart.cart
    if not cart_obj or cart.is_empty():
        data = {
            'success': False,
            'message': u'Корзина пуста!',
        }
        return HttpResponse(json.dumps(data), mimetype='application/json')

    form = OrderNoRegForm(request.POST)
    data = None

    if form.is_valid():
        data = {
            'success': form.is_valid(),
            'form_errors': '',
            'message': u'Спасибо за ваш заказ, мы свяжемся с вами в ближайшее время.',
            'redirect': reverse('cart'),
        }

        # создаём заказ
        order = OrderNoReg.objects.create(
            name = form.cleaned_data['name'],
            phone = form.cleaned_data['phone'],
            sum = cart.cost_with_global_discount(),  # учесть общую скидку, если она есть
        )

        # скопировать покупки из корзины в заказ
        for cart_item in cart_obj.get_items():
            if cart_item.quantity < 1:
                continue

            OrderNoRegItem.objects.create(
                order = order,
                good = cart_item.product,
                price = cart_item.price,
                count = cart_item.quantity
            )

        try:
            send_order_noreg_mail(order)  # отправить e-mail сообщение группе менеджеров
        except:
            mail_admins(
                subject=u'Ошибка отправки уведомления менеджерам',
                message=u'Заказ № %s (без регистрации).\n%s' % (order.pk, traceback.format_exc(),)
            )

        cart_obj.delete()  # удалить корзину

    if not data:
        data = {
            'success': form.is_valid(),
            'field_errors': form.errors,
            'form_errors': form.non_field_errors(),
            'message': u'',
        }

    return HttpResponse(json.dumps(data), mimetype='application/json')


@staff_member_required
def export_goods(request):
    """Экспорт всех товаров в формате Excel."""
    # индексы колонок в xls
    IDX_CHANGE = 0
    IDX_PRODUCER = 1
    IDX_NAME = 2
    IDX_ARTICUL = 3
    IDX_CATEGORY = 4
    IDX_DIMS = 5
    IDX_SALE = 6 # aka special
    IDX_NEW = 7
    IDX_DESCRIPTION = 8

    # параметры колонок (заголовок, ширина)
    columns = [
        (u'Изменить?', 11),
        (u'Производитель', 30),
        (u'Наименование товара', 40),
        (u'Ном. номер', 15),
        (u'Категория', 16),
        (u'Размер', 20),
        (u'Распродажа?', 13),
        (u'Новинка?', 10),
        (u'Описание', 100),
    ]

    book = xlwt.Workbook(encoding='cp1251', style_compression=2)
    sh = book.add_sheet(datetime.datetime.now().strftime('%d.%m.%y'), cell_overwrite_ok=True)

    # стиль для вывода артикулов
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_RIGHT
    articul_style = xlwt.XFStyle()
    articul_style.alignment = alignment

    # вывести названия колонок и задать им ширину
    for i, col in enumerate(columns):
        sh.write(0, i, col[0])
        sh.col(i).width = col[1]*256

    # заполнить данными
    queryset = Good.objects.all().order_by('articul', 'name')
    for ri, good in enumerate(queryset, start=1):
        #cats = sorted(good_cats.get(good.pk, []))
        sh.write(ri, IDX_CHANGE, '')
        sh.write(ri, IDX_PRODUCER, unicode(good.producer))
        sh.write(ri, IDX_NAME, good.name)
        sh.write(ri, IDX_ARTICUL, good.articul, articul_style)
        sh.write(ri, IDX_CATEGORY, good.category_id or '')
        sh.write(ri, IDX_DIMS, good.dims)
        sh.write(ri, IDX_SALE, '+' if good.special else '')
        sh.write(ri, IDX_NEW, '+' if good.new else '')
        sh.write(ri, IDX_DESCRIPTION, good.description)

    # сохранить книгу
    f = StringIO()
    book.save(f)
    xls_content = f.getvalue()
    f.close()

    # ответ
    response = HttpResponse(xls_content, mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="sklad51_goods.xls"'
    return response
