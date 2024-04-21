# -*- coding: utf-8 -*-
import logging
from email.header import Header

from django.template.loader import render_to_string
from django.core.mail import EmailMessage

import models


log = logging.getLogger('partners')


def send_mail_message(obj):
    recipients = models.Recipients.objects.values_list('email', flat=True)
    if not recipients:
        log.error('send_mail_message - No Recipients.')
        return

    template = 'partners/mail_message.txt'
    subject = u'Новое сообщение о партнерстве'

    email_body = render_to_string(template, {'obj': obj})
    email = EmailMessage(subject=subject, to=recipients, body=email_body)
    return email.send(fail_silently=True) # ignore errors
