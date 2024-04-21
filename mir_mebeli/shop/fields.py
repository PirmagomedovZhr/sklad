# -*- coding: utf-8 -*-
from django import forms
from django.utils.encoding import smart_unicode


class TreeNodeChoiceField(forms.ModelChoiceField):
    """A ModelChoiceField for MPTT tree nodes.

        Адаптированный класс из mptt.forms.TreeNodeChoiceField.
    """
    def __init__(self, level_indicator=u'---', *args, **kwargs):
        self.level_indicator = level_indicator
        #kwargs['empty_label'] = None  # не удалять пустой вариант выбора!
        super(TreeNodeChoiceField, self).__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        """
        Creates labels which represent the tree level of each node when
        generating option labels.
        """
        return u'%s %s' % (self.level_indicator * getattr(obj, obj._meta.level_attr), smart_unicode(obj))
