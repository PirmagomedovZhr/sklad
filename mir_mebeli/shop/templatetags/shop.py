# -*- coding: utf-8 -*-
from django import template
from django.template.defaultfilters import stringfilter

from mir_mebeli.shop.models import Category, Good
from mir_mebeli.shop.forms import SearchForm


register = template.Library()


@register.filter
@stringfilter
def price(value):
    str_len = len(value)
    offset = str_len % 3
    groups = [value[i:i+3] for i in xrange(offset, str_len, 3)]
    if offset:
        groups.insert(0, value[0:offset])
    return ' '.join(groups)


@register.inclusion_tag('cms/parts/specials.html')
def render_specials():
    return {'specials': Good.objects.filter(special=True),}


@register.inclusion_tag('cms/parts/catalog/categories.html')
def render_categories(all=False):
    """Вывести категории. По умолчанию, только базовые."""
    if not all:
        #categories = Category.objects.filter(basic=True, count_all__gt=0, hidden=False).order_by('order', 'name')
        categories = Category.objects.filter(basic=True, hidden=False).order_by('order', 'name')
    else:
        #categories = Category.objects.filter(count_all__gt=0, hidden=False).order_by('order', 'name')
        categories = Category.objects.filter(hidden=False).order_by('order', 'name')
    return {'categories': categories,}


@register.inclusion_tag('cms/parts/catalog/category_popup.html', takes_context=True)
def render_category_popup(context):
    """Вывести базовые категории для попапа."""
    return {
        'categories': Category.objects.filter(basic=True, hidden=False).order_by('order', 'name'),
        'root_category': context.get('root_category'),
    }


@register.inclusion_tag('cms/parts/search_form.html')
def render_search_form(request):
    """Поисковая форма."""
    initial = {
        'q': request.GET.get('q'),
        'cat': request.GET.get('cat'),
    }
    form = SearchForm(initial=initial)

    try:
        cat_id = int(initial['cat'])
        cat_choices = dict(form.fields['cat'].choices)
        current_cat_name = cat_choices.get(cat_id, '')
    except (TypeError, ValueError):
        current_cat_name = ''

    return {'search_form': form, 'current_cat_name': current_cat_name,}
