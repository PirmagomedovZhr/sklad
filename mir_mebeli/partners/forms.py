# -*- coding: utf-8 -*-
from django import forms

from supercaptcha import CaptchaField

from models import Message


class MessageForm(forms.ModelForm):
    captcha = CaptchaField(label=u"Код с картинки")

    class Meta:
        model = Message
        fields = ['name', 'phone', 'email', 'body', 'file1', 'file2', 'file3', 'file4']

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        file_fields = ['file1', 'file2', 'file3', 'file4']
        for fn in file_fields:
            self.fields[fn].label = u''
        self.fields[file_fields[0]].label = u'Прикрепить файлы'
