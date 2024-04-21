# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from django.views.decorators.http import require_GET
from django.core.urlresolvers import reverse
from django.http import Http404

from mir_mebeli.shop.models import Category, Good
from mir_mebeli.shop.forms import SearchForm
from mir_mebeli.utilities.my_pagination import _paginate


def _catalog_breadcrumb(request, category, include_self=True):
    """Breadcrumbs для текущей категории каталога."""
    ancestors = [{'url': '/', 'title': u'Каталог строительных материалов'}]
    ancestors += [{'url': cat.get_absolute_url(), 'title': cat.name} for cat in category.get_ancestors()]
    if include_self:
        ancestors.append({'url': category.get_absolute_url(), 'title': category.name})
    return {'catalog_breadcrumb': ancestors}


def category(request, category_path=None):
    """Все товары внутри категории и в её подкатегориях.
    """
    category = get_object_or_404(Category, path=category_path, hidden=False)

    _sub_categories = category.get_descendants().filter(hidden=False).order_by('order', 'name')
    _category_ids = [_cat.pk for _cat in _sub_categories]
    _category_ids.append(category.pk)

    goods_list = (Good.objects.filter(is_available=True).filter(category__in=_category_ids)
        .extra(select={'ordering_name': "CASE WHEN display_name <> '' THEN display_name ELSE name END"})
        .order_by('ordering_name')
    )

    root_category = category.get_root()
    root_sub_categories = root_category.get_descendants().filter(count_all__gt=0).filter(hidden=False).order_by('order', 'name')

    extra_context = {
        'category': category,
        'goods_list': goods_list,
        'root_category': root_category,
        'root_sub_categories': root_sub_categories,
    }

    if request.is_ajax():
        template = 'cms/pages/goods_list.html'
    else:
        template = 'cms/pages/category.html'
        extra_context.update(_catalog_breadcrumb(request, category))

    return direct_to_template(request, template, extra_context)


def good(request, category_path=None, good_id=None):
    """Товар."""
    category = get_object_or_404(Category, path=category_path)
    good = get_object_or_404(category.goods, id=good_id)

    def _get_root_category():
        root_category = category
        if not root_category.basic:
            cat_parents = category.get_ancestors().filter(basic=True)
            if cat_parents and cat_parents[0]:
                root_category = cat_parents[0]
        return root_category

    root_category = _get_root_category()

    extra_context = {
        'category': category,
        'good': good,
        'root_category': root_category,
    }

    # если category подрубрика, то взять все товары внутри нее
    sub_category_goods = None
    if not category.basic:
        sub_category_goods = category.goods.all().order_by('name')

    try:
        sub_category_goods_index = [index for index, x in enumerate(sub_category_goods, start=1) if x.pk == good.pk][0]
    except (ValueError, IndexError, TypeError) as e:
        sub_category_goods_index = None

    extra_context['sub_category_goods'] = sub_category_goods
    extra_context['sub_category_goods_index'] = sub_category_goods_index
    #extra_context.update(_catalog_breadcrumb(request, category, include_self=True))
    return direct_to_template(request, 'cms/pages/good_popup.html', extra_context)


@require_GET
def search(request):
    search_form = SearchForm(data=request.GET)
    extra_context = {'search_form': search_form,}

    if search_form.is_valid():
        query = search_form.cleaned_data.get('q')
        cat = search_form.cleaned_data.get('cat')

        try:
            category = Category.objects.get(pk=int(cat))
        except (TypeError, ValueError, Category.DoesNotExist):
            category = None

        if cat:
            results = Good.indexer.search(u'%s AND "%s"' % (query, cat.name,)).prefetch().spell_correction()
        else:
            results = Good.indexer.search(query).prefetch().spell_correction()

        extra_context['category'] = category
        extra_context['total_found'] = len(results)
        extra_context['maybe'] = results.get_corrected_query_string()
        extra_context.update(_paginate(request, results))

    return direct_to_template(request, 'cms/pages/search.html', extra_context)
