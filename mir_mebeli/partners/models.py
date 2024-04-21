# -*- coding: utf-8 -*-
import os
import hashlib

from django.db import models
from django.utils.encoding import smart_str
from django.conf import settings


UPLOAD_ROOT = getattr(settings, 'PARTNERS_UPLOAD_ROOT', 'partners')

_HASH_FIELDS = ['name', 'phone', 'email']


def upload_to(path, new_filename=None):
    """Куда и под каким именем сохранить загруженный файл."""
    def get_upload_path(instance, filename):
        filename = new_filename or filename
        _key = u''.join([getattr(instance, fn, u'') for fn in _HASH_FIELDS])
        _hash = hashlib.md5(smart_str(_key)).hexdigest()
        return os.path.join(path, _hash, filename)
    return get_upload_path


class Message(models.Model):
    """Предложение о партнерстве."""
    name = models.CharField(u'ваше имя', max_length=100)
    phone = models.CharField(u'телефон', max_length=100)
    email = models.EmailField(u'электронная почта')
    body = models.TextField(u'ваше сообщение', max_length=2000, blank=True, default='')

    file1 = models.FileField(u'файл 1', max_length=200, upload_to=upload_to(UPLOAD_ROOT), blank=True, default='')
    file2 = models.FileField(u'файл 2', max_length=200, upload_to=upload_to(UPLOAD_ROOT), blank=True, default='')
    file3 = models.FileField(u'файл 3', max_length=200, upload_to=upload_to(UPLOAD_ROOT), blank=True, default='')
    file4 = models.FileField(u'файл 4', max_length=200, upload_to=upload_to(UPLOAD_ROOT), blank=True, default='')

    created_at = models.DateTimeField(u'создано', auto_now_add=True)
    updated_at = models.DateTimeField(u'изменено', auto_now=True)

    class Meta:
        verbose_name = u'сообщение'
        verbose_name_plural = u'сообщения о партнерстве'

    def __unicode__(self):
        return u'%s, %s, %s, %s' % (self.name, self.phone, self.email, self.created_at)

    def files(self):
        return [f for f in (self.file1, self.file2, self.file3, self.file4) if f and hasattr(f, "url")]


class Recipients(models.Model):
    """Получатели уведомлений."""
    email = models.EmailField(u'email', unique=True)

    class Meta:
        verbose_name = u'получатель уведомлений'
        verbose_name_plural = u'получатели уведомлений'
        ordering = ['email']

    def __unicode__(self):
        return self.email
