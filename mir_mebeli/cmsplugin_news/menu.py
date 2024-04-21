from datetime import datetime
from menus.base import Menu, NavigationNode
from django.core.urlresolvers import NoReverseMatch, reverse
from menus.menu_pool import menu_pool
from cms.app_base import CMSApp
from django.utils.translation import ugettext_lazy as _
from cms.menu_bases import CMSAttachMenu
from cmsplugin_news.models import News
from pytils.dt import ru_strftime
 
class NewsMenu(CMSAttachMenu):
    
    name = _("News")
    
    def get_nodes(self, request):
        res = []
        nodes = []
        
        items = News.published.all()
        
        years_done = []
        months_done = []
        days_done = []
        slug_done = []
        
        for item in items:
            date = item.pub_date
            
            if not date.year in years_done:
                years_done.append(date.year)
                year_node = NavigationNode(date.year, reverse('news_archive_year', kwargs=dict(year=date.year)), 'news-%s' % date.year, None, 'news')
                # year_node = NavigationNode(date.year, reverse('news_archive_year', kwargs=dict(year=date.year)))
                # year_node.childrens = []
                # months_done = []
                # res.append(year_node)
                nodes.append(year_node)
            
            if not date.month in months_done:
                months_done.append(date.month)
                month_node = NavigationNode(ru_strftime(date=date, format=u'%B'), reverse('news_archive_month', kwargs=dict(year=date.year, month=datetime.strftime(date, '%m'))), 'news-%s-%s' % (date.year, datetime.strftime(date, '%m')), 'news-%s' % date.year, 'news')
                # month_node = NavigationNode(datetime.strftime(date, '%B'), 
                #                     reverse('news_archive_month', kwargs=dict(
                #                         year=date.year, 
                #                         month=datetime.strftime(date, '%m'))))
                # month_node.childrens = []
                # days_done = []
                # year_node.childrens.append(month_node)
                nodes.append(month_node)
            
            if not date.day in days_done:
                days_done.append(date.day)
                day_node = NavigationNode(datetime.strftime(date, '%d'),
                                    reverse('news_archive_day', kwargs=dict(
                                        year=date.year,
                                        month=datetime.strftime(date, '%m'),
                                        day=datetime.strftime(date, '%d'))),
                                    'news-%s-%s-%s' % (date.year, datetime.strftime(date, '%m'), datetime.strftime(date, '%d')), 'news-%s-%s' % (date.year, datetime.strftime(date, '%m')), 'news')
                # day_node = NavigationNode(datetime.strftime(date, '%d'), 
                #                     reverse('news_archive_day', kwargs=dict(
                #                         year=date.year, 
                #                         month=datetime.strftime(date, '%m'),
                #                         day=datetime.strftime(date, '%d'))))
                # day_node.childrens = []
                # slug_done = []
                # month_node.childrens.append(day_node)
                nodes.append(day_node)
            
            if not item.slug in slug_done:
                slug_done.append(item.slug)
                item_node = NavigationNode(item.title, item.get_absolute_url(), 'news-item-%d' % item.pk, 'news-%s-%s-%s' % (date.year, datetime.strftime(date, '%m'), datetime.strftime(date, '%d')), 'news')
                # item_node = NavigationNode(item.title, item.get_absolute_url())
                # item_node.childrens = []
                # day_node.childrens.append(item_node)
                nodes.append(item_node)
            
        return nodes
    
menu_pool.register_menu(NewsMenu)
