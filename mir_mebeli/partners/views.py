# -*- coding: utf-8 -*-
from django.views.decorators.http import require_http_methods, require_GET
from django.views.decorators.csrf import csrf_protect
from django.views.generic.simple import direct_to_template
from django.shortcuts import redirect

from forms import MessageForm
from emails import send_mail_message


@require_http_methods(['GET', 'POST'])
@csrf_protect
def index(request):
    form_class = MessageForm
    success_url = 'partners-thanks'

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            message = form.save()
            send_mail_message(message)
            return redirect(success_url)
    else:
        form = form_class()

    return direct_to_template(request, 'partners/partners.html', {'form': form})


@require_GET
def thanks(request):
    return direct_to_template(request, 'partners/partners_thanks.html')


def notify(request, message):
    pass
