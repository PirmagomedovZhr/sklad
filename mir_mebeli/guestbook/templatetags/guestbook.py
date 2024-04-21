# -*- coding: utf-8 -*-

from django import template
from mir_mebeli.guestbook.models import Message
import re

register = template.Library()

@register.tag(name="get_messages")
def do_get_messages(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    m = re.search(r'as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name
    args = m.groups()
    return GetMessages(args[0])

class GetMessages(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        context[self.var_name] = Message.objects.filter(status='P').order_by("-created", "-id")
        # if context['current_page'] and not isinstance(context['current_page'], str):
        #     # context[self.var_name] = Item.objects.filter(category=context['current_page'].id).order_by('title')
        # else:
        #     # context[self.var_name] = []
        return ''
