# -*- coding: utf-8 -*-

from django.test import TestCase
from shop.models import Category, Shop, Good, Available
from django.db.models.aggregates import Sum

class CategoryTest(TestCase):
    def create_some_shops(self):
        self.shop_1 = Shop(name=u"Склад", region=False, online=False)
        self.shop_1.save()
        self.shop_2 = Shop(name=u"Интернет–магазин", region=False, online=True)
        self.shop_2.save()
        self.shop_3 = Shop(name=u"Областной магазин", region=True, online=False)
        self.shop_3.save()

    def create_some_categories(self):
        self.cat_1 = Category(name=u' 1  Мягкая мебель',basic=True)
        self.cat_1.save()
        self.cat_2 = Category(name=u" 2  Новинки",basic=True)
        self.cat_2.save()
        self.cat_1_1 = Category(name=u"1_1 Кресла",parent=self.cat_1,basic=False)
        self.cat_1_1.save()
        self.cat_1_2 = Category(name=u"1_2 Диван-кровати",parent=self.cat_1,basic=False)
        self.cat_1_2.save()
        self.cat_1_3 = Category(name=u"1_3 Кушетки",parent=self.cat_1,basic=False)
        self.cat_1_3.save()

    def create_some_goods(self):
        self.good_1 = Good(name=u"Товар номер один", articul="000001")
        self.good_1.save()
        self.good_1.categories=[self.cat_1_1]
        self.good_1.categories.add(self.cat_1_3)
        self.good_1.categories.add(self.cat_2)
        self.good_1.categories=[self.cat_1_3, self.cat_1_2]
                                                                        
        self.good_2 = Good(name=u"Товар номер два", articul="000002")
        self.good_2.save()
        self.good_2.categories=[self.cat_1]

        self.good_3 = Good(name=u"Товар номер три", articul="000003")
        self.good_3.save()
        self.good_3.categories=[self.cat_1_3]

        self.good_4 = Good(name=u"Товар номер четыре", articul="000004")
        self.good_4.save()
        self.good_4.categories=[self.cat_1_3]

        av_1 = Available(good=self.good_1, shop=self.shop_1, count=1, price=100)
        av_1.save()
        av_2 = Available(good=self.good_1, shop=self.shop_2, count=1, price=100)
        av_2.save()
        av_3 = Available(good=self.good_2, shop=self.shop_2, count=1, price=100)
        av_3.save()

        av_2.delete()

        self.good_1.delete()
        self.good_2.delete()
        self.good_3.delete()
        self.good_4.delete()

    def test_1_categories_count(self):
        self.create_some_categories()
        self.failUnlessEqual(Category.objects.count(), 5)

    def test_2_subcategories_count(self):
        self.create_some_categories()
        self.failUnlessEqual(self.cat_1.category_set.count(), 3)

    def test_3_good_count_in_category(self):
        self.create_some_categories()
        self.create_some_shops()
        self.create_some_goods()
        self.failUnlessEqual(Category.objects.aggregate (Sum('count_all'), Sum('count_online')), {'count_all__sum': 0, 'count_online__sum': 0})

#__test__ = {"doctest": """
#Another way to test that 1 + 1 is equal to 2.
#
#>>> 1 + 1 == 2
#True
#"""}
#