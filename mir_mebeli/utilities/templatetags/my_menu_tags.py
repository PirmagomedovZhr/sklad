# -*- coding: utf-8 -*-
from django import template


register = template.Library()


@register.filter
def parent_namespace(nodes, namespace):
    """Возвращает только те ноды меню, которые находятся в указанном пространстве имен."""
    return [n for n in nodes if n.parent_namespace == namespace]
