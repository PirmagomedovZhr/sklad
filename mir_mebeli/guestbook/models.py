# -*- coding: utf-8 -*-

from django.db import models

# from basic.people.models import Person

class Message(models.Model):
    STATUS_CHOICES = (
        ('P', u'Опубликовано'),
        ('N', u'Не опубликовано'),
    )
    status = models.CharField(u"статус", max_length=1, choices=STATUS_CHOICES, default='P')
    fio = models.CharField(u"автор", max_length=100)
    email = models.CharField(u"e–mail", max_length=30)
    text = models.TextField(u"текст", blank=True, null=True)
    created = models.DateTimeField(u"добавлено", auto_now_add=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.fio, self.status)
    
    class Meta:
        verbose_name = u'сообщение'
        verbose_name_plural = u'сообщения гостевой'
