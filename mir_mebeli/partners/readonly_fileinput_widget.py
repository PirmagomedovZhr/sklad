# -*- coding: utf-8 -*-
import os

from django import forms
from django.utils.safestring import mark_safe


class ReadonlyFileInput(forms.Widget):
    def render(self, name, value, attrs=None):
        if value and hasattr(value, "url"):
            return mark_safe(u'<p><a target="_blank" href="%s">%s</a></p>' % (value.url, os.path.basename(value.path)))
        else:
            return ''
