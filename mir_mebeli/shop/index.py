# -*- coding: utf-8 -*-
from djapian import space, Indexer

from shop.models import Good


def filter_goods(indexer, obj):
    """Только товары, которые:
        - прикреплены к какой-нибудь рубрике и
        - не входят ни в одну из скрытых рубрик
	- есть в наличии
    """
    return obj.category_id and not obj.any_hidden_category and obj.is_available


class GoodIndexer(Indexer):
    fields = ['category', 'display_name', 'name', 'description', 'articul', 'producer']
    tags = [
        ('category', 'category', 2),
        ('display_name', 'display_name', 3),
        ('name', 'name', 4),
        ('description', 'description', 5),
        ('producer', 'producer'),
        ('articul', 'articul'),
    ]
    trigger = filter_goods

space.add_index(Good, GoodIndexer, attach_as='indexer')
