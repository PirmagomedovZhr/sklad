# -*- coding: utf-8 -*-
from django.template import Library

from ..models import Teaser


register = Library()


@register.inclusion_tag('cms/parts/teasers.html', takes_context=True)
def render_teasers(context):
    context['teasers'] = Teaser.objects.get_teasers()
    return context
