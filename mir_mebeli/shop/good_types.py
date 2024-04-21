# -*- coding: utf-8 -*-


# все поля, которые могут встретиться в типах товаров
GOOD_FIELDS = {
    'producer': u'Производитель',
    'brand': u'Бренд',
    'weight': u'Масса',
    'color': u'Цвет',
    'usage_area': u'Область применения',
    'expense': u'Расход материала',
    'dims': u'Размер',
    'amount': u'Количество в упаковке',
    'units': u'Единица измерения',
}


# какие поля показывать по умолчанию, если тип товара не выбран
DEFAULT_GOOD_FIELDS = (
    'producer',
    'brand',
    'weight',
    'color',
    'usage_area',
    'expense',
    'amount',
    'dims',
    'units',
)


# типы товаров
GOOD_TYPES = {
    'grunt': {
        'name': u'Грунт',
        'fields': (
            'producer',
            'brand',
            'weight',
            'color',
            'usage_area',
            'expense',
        ),
    },
    'emal': {
        'name': u'Эмаль',
        'fields': (
            'producer',
            'brand',
            'weight',
            'color',
            'usage_area',
        ),
    },
    'gazobeton': {
        'name': u'Газобетон',
        'fields': (
            'producer',
            'weight',
            'dims',
            'amount',
        ),
    },
}


# варианты выбора типа товара
GOOD_TYPE_CHOICES = [(k, v['name']) for k,v in sorted(GOOD_TYPES.items(), key=lambda t: t[0])]
