# -*- coding: utf-8 -*-
# django-mptt enabled FilteredSelectMultiple m2m widget
# you will also need mptt_m2m_selectbox.js
#
# based on:
# http://anentropic.wordpress.com/2009/11/05/more-django-mptt-goodness-filteredselectmultiple-m2m-widget/
# http://djangosnippets.org/snippets/1779/
# http://djangosnippets.org/snippets/1780/

from itertools import chain

import django
from django import forms
from django.contrib.admin import widgets
from django.utils.encoding import smart_unicode, force_unicode
from django.utils.html import escape, conditional_escape
from django.conf import settings


if django.VERSION >= (1, 3, 0):
    JS_ROOT_URL = settings.STATIC_URL
else:
    JS_ROOT_URL = settings.MEDIA_URL


class MPTTModelChoiceIterator(forms.models.ModelChoiceIterator):
    def choice(self, obj):
        tree_id = getattr(obj, getattr(self.queryset.model._meta, 'tree_id_atrr', 'tree_id'), 0)
        left = getattr(obj, getattr(self.queryset.model._meta, 'left_atrr', 'lft'), 0)
        return super(MPTTModelChoiceIterator, self).choice(obj) + ((tree_id, left),)


class MPTTModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        level = getattr(obj, getattr(self.queryset.model._meta, 'level_attr', 'level'), 0)
        ancestors = obj.get_ancestors() # extra query per instance. maybe optimize?
        if ancestors:
            path_names = [smart_unicode(p.name) for p in ancestors]
            path_names.append(smart_unicode(obj))
            path = ' / '.join(path_names)
            return u'%s %s (%s)' % ('-' * level, path, obj.pk)
        else:
            return u'%s %s (%s)' % ('-' * level, smart_unicode(obj), obj.pk,)

    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices
        return MPTTModelChoiceIterator(self)

    choices = property(_get_choices, forms.ChoiceField._set_choices)


class MPTTFilteredSelectMultiple(widgets.FilteredSelectMultiple):
    def __init__(self, verbose_name, is_stacked, attrs=None, choices=()):
        super(MPTTFilteredSelectMultiple, self).__init__(verbose_name, is_stacked, attrs, choices)

    def render_options(self, choices, selected_choices):
        """
        this is copy'n'pasted from django.forms.widgets Select(Widget)
        change to the for loop and render_option so they will unpack and use our extra tuple of mptt sort fields
        (if you pass in some default choices for this field, make sure they have the extra tuple too!)
        """
        def render_option(option_value, option_label, sort_fields):
            option_value = force_unicode(option_value)
            selected_html = (option_value in selected_choices) and u' selected="selected"' or ''
            return u'<option value="%s" data-tree-id="%s" data-left-value="%s"%s>%s</option>' % (
                escape(option_value),
                sort_fields[0],
                sort_fields[1],
                selected_html,
                conditional_escape(force_unicode(option_label)),
            )
        # Normalize to strings.
        selected_choices = set([force_unicode(v) for v in selected_choices])
        output = []
        for option_value, option_label, sort_fields in chain(self.choices, choices):
            if isinstance(option_label, (list, tuple)):
                output.append(u'<optgroup label="%s">' % escape(force_unicode(option_value)))
                for option in option_label:
                    output.append(render_option(*option))
                output.append(u'</optgroup>')
            else:
                output.append(render_option(option_value, option_label, sort_fields))
        return u'\n'.join(output)

    class Media:
        extend = False
        js = (
            settings.ADMIN_MEDIA_PREFIX + "js/core.js",
            JS_ROOT_URL + "js/mptt_m2m_selectbox.js", # !!!
            settings.ADMIN_MEDIA_PREFIX + "js/SelectFilter2.js",
        )
