# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand
from django.core.mail import get_connection, EmailMessage
from django.conf import settings

from mailing.models import Message


MAX_ATTEMPTS = getattr(settings, 'MAILING_MAX_ATTEMPTS', 2)
FROM_EMAIL = getattr(settings, 'MAILING_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)


class Command(NoArgsCommand):
    help = u'Отправляет неотправленные письма.'

    def handle_noargs(self, **options):
        connection = get_connection()
        connection.open()

        messages = Message.objects.filter(sent=False, attempts__lt=MAX_ATTEMPTS).order_by('created_at')
        for msg in messages:
            try:
                email = EmailMessage(subject=msg.subject, body=msg.text, from_email=FROM_EMAIL, to=[msg.to],
                    connection=connection)
                email.send()
                msg.sent = True
            except:
                msg.sent = False
                continue
            finally:
                msg.attempts += 1
                msg.save()

        connection.close()
