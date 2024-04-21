# -*- coding: utf-8 -*-

from django import template
from django.template.defaultfilters import stringfilter
# import datetime

register = template.Library()

@register.simple_tag
def show_errors_as_json(form):
    from django.utils import simplejson
    result = dict(success=form.is_valid(), fields=dict(), errors=u'%s' % form.non_field_errors())
    for field in form.visible_fields():
        result['fields'].update({ field.name: not field.errors })
    return simplejson.dumps(result)
