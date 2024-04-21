# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.http import Http404
from django.conf import settings

from cms.sitemaps.cms_sitemap import CMSSitemap
from cms.apphook_pool import apphook_pool
from cms.views import details

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

try:
    import djapian
    djapian.load_indexes()
except:
    pass

from mir_mebeli.shop.categories import views as cat_views


def anyview(request, *args, **kwargs):
    url_name = kwargs.pop('url_name', None)

    try:
        # try mir_mebeli.shop.categories urls
        if url_name:
            if url_name == 'search':
                return cat_views.search(request)
            elif url_name == 'category_view':
                return cat_views.category(request, **kwargs)
            elif url_name == 'good_view':
                return cat_views.good(request, **kwargs)
    except Http404:
        pass # maybe this is cms url

    cms_kwargs = {'slug': '',}
    if 'slug' not in kwargs and 'category_path' in kwargs:
        cms_kwargs['slug'] = kwargs['category_path']

    # try cms urls
    return details(request, **cms_kwargs)


urlpatterns = patterns('',
    # Example:
    # (r'^mir_mebeli/', include('mir_mebeli.foo.urls')),
    url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': {'cmspages': CMSSitemap}}),
    url(r'^robots\.txt$', direct_to_template, {'template': 'robots.txt', 'mimetype': 'text/plain'}),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    (r'^comments/', include('django.contrib.comments.urls')),

    (r'^korzina/', include('mir_mebeli.cart.urls')),

    (r'^wishlist/', include('mir_mebeli.wishlist.urls')),

    url(r'^order/checkout/$', 'mir_mebeli.shop.views.order_checkout', name='shop-order-checkout'),
    url(r'^order/confirm/$', 'mir_mebeli.shop.views.order_confirm', name='shop-order-confirm'),
    url(r'^order/go-bank/(?P<order_id>\d+)$', 'mir_mebeli.shop.views.order_go_bank', name='shop-order-go-bank'),
    url(r'^order/done/(?P<order_id>\d+)/$', 'mir_mebeli.shop.views.order_done', name='shop-order-done'),
    url(r'^order/cancel/(?P<order_id>\d+)/$', 'mir_mebeli.shop.views.order_cancel', name='shop-order-cancel'),
    url(r'^order/info/(?P<order_id>\d+)/$', 'mir_mebeli.shop.views.order_info', name='shop-order-info'),
    url(r'^order/success/$', 'mir_mebeli.shop.views.success_payment', name='shop-order-success'),
    url(r'^order/fail/$', 'mir_mebeli.shop.views.fail_payment', name='shop-order-fail'),
    url(r'^order/noreg/$', 'mir_mebeli.shop.views.order_noreg', name='shop-order-noreg'),

    url(r'^logout/$', 'mir_mebeli.shop.views.logout', name="logout_buyer"),

    url(r'^register-and-login/$', 'mir_mebeli.shop.views.register_and_login', name='register-and-login'),
    url(r'^register-agreement/$', direct_to_template, {'template': 'cms/pages/auth/register_agreement.html'},
        name='register-agreement'),

    # url(r'^req_price/(?P<good_id>\d+)/$', 'mir_mebeli.shop.views.req_price', name="req_price"),
    url(r'^req-phone-call/$', 'mir_mebeli.shop.views.req_phone_call', name="req-phone-call"),

    url(r'^sitemap/$', 'mir_mebeli.sitemap.views.sitemap', name="sitemap"),

    url(r'^profile/edit/$', 'mir_mebeli.shop.views.profile_edit', name='profile-edit'),
    url(r'^change/password/$','mir_mebeli.shop.views.change_password', name='change-password'),

    url(r'^psbank/', include('psbank.urls')),

    # url(r'^korzina/psbank/(?P<order_id>\d+)/$', 'mir_mebeli.shop.views.show_psbank_payment_info',
    #     name='shop-psbank-payment-info'),

    url(r'^api/export-goods/$', 'mir_mebeli.shop.views.export_goods', name='shop-export-goods'),

    url(r'^error/no-buyer-profile/$', login_required(direct_to_template), {'template': 'error/no_buyer_profile.html'},
        name='error_no_buyer_profile'),
    url(r'^yandex-money/', include('yandex_money.urls')),

#    url(r'^', include('cms.urls')),
)


# ссылки каталога и корень cms.
# всё, кроме pages-root, завязано на anyview.
# переменная url_name нужна, чтобы определить какой из паттернов сработал.
cat_urlpatterns = patterns('',
    url(r'^search/$', anyview, kwargs={'url_name': 'search'}, name="search"),

    url(r'^(?P<category_path>.+)/$', anyview, kwargs={'url_name': 'category_view'}, name="category_view"),

    url(r'^(?P<category_path>.+)/(?P<good_id>\d+)\.html$', anyview, kwargs={'url_name': 'good_view'}, name="good_view"),

    # cms
    url(r'^(?P<slug>[0-9A-Za-z-_.//]+)/$', anyview),
    url(r'^$', details, {'slug':''}, name='pages-root'),
)


# подключить ссылки из cms-приложений
if apphook_pool.get_apphooks():
    from cms.appresolver import get_app_patterns
    cat_urlpatterns = get_app_patterns() + cat_urlpatterns


urlpatterns += cat_urlpatterns

if settings.DEBUG:
    urlpatterns = patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    ) + urlpatterns
