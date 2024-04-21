# -*- coding: utf-8 -*-
from forms import ReqPriceForm, ReqPhoneCallForm, LoginForm, ResetPasswordForm, RegistrationForm
from models import Buyer
import category_menu


def shop(request):
    assert hasattr(request, 'user'), "Not found django.contrib.auth.middleware.AuthenticationMiddleware"

    req_price_initial = {}
    if request.user.is_authenticated():
        try:
            buyer = request.user.buyer
            req_price_initial['phone'] = buyer.phone
            req_price_initial['email'] = buyer.email
        except Buyer.DoesNotExist:
            pass

    context = {
        'dialogs': {
            # 'req_price': ReqPriceForm(initial=req_price_initial),
        },
        'req_phone_call_form': ReqPhoneCallForm(),
    }

    if not request.user.is_authenticated():
        context['dialogs'].update({
            'login_form': LoginForm(prefix='login'),
            'register_form': RegistrationForm(prefix='register'),
            'reset_form': ResetPasswordForm(prefix='reset'),
            'next': request.path,
        })

    return context


def catalog_category_menu(request):
    """Основные рубрики и их подрубрики. Для показа в главном меню и на карте сайта."""
    return {'catalog_category_menu': category_menu.get_menu(request)}


def pagination(request):
    try:
        page = int(request.REQUEST['page'])
    except (KeyError, ValueError, TypeError):
        page = 1
    try:
        per_page = int(request.REQUEST['pp'])
    except (KeyError, ValueError, TypeError):
        per_page = request.session.get('per_page', default=15)
    request.session['per_page'] = per_page
    return {'pagination': {'page': page, 'per_page': per_page}}
