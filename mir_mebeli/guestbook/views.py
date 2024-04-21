# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.views.generic.simple import direct_to_template
from django.conf import settings

from mir_mebeli.guestbook.models import Message
from mir_mebeli.shop.forms import MessageForm
from mir_mebeli.shop.models import get_manager_emails
from mir_mebeli.utilities.my_pagination import _paginate


SHOP_SETTINGS = getattr(settings, 'SHOP_SETTINGS')


def add(request):
    if request.POST:
        form = MessageForm(request.POST)

        if form.is_valid() and form.cleaned_data['phone']:
            return HttpResponseRedirect(reverse('guestbook-index'))

        if form.is_valid() and not form.cleaned_data['phone']:
            message = Message(
                fio = form.cleaned_data['fio'],
                email = form.cleaned_data['email'],
                text = form.cleaned_data['text']
            )
            message.save()

            subject = u'Добавлено новое сообщение в гостевую книгу сайта sklad51.ru'
            email_msg = render_to_string('mail/message.txt', {'msg': message,})
            email_sender = SHOP_SETTINGS['EMAIL_SENDER']
            recipients = get_manager_emails()

            send_mail(subject, email_msg, email_sender, recipients, fail_silently=True)

            return HttpResponseRedirect(reverse('guestbook-index'))
    else:
        form = MessageForm()

    messages = Message.objects.filter(status="P").order_by("-created") # only published messages

    extra_context = {
        "form": form,
        'pagination_form_text': u'Вывести по',
    }
    extra_context.update(_paginate(request, messages))

    return direct_to_template(request, 'cms/pages/guestbook.html', extra_context)
