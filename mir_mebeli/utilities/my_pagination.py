# -*- coding: utf-8 -*-
from django.http import Http404
from django.core.paginator import EmptyPage, Paginator
from django.conf import settings

from pagination.templatetags.pagination_tags import paginate


_DEFAULTS = {
    'PER_PAGE': 24,
    'ALLOWED_VALUES': (12, 24, 48, 96),
    'ORPHANS': 2,
}

conf = _DEFAULTS.copy()
conf.update(getattr(settings, 'PAGINATION_SETTINGS', {}))


def _paginate(request, obj_list):
    try:
        per_page = int(request.REQUEST.get('pp', default=request.session.get('per_page', default=conf['PER_PAGE'])))
    except:
        per_page = conf['PER_PAGE']

    if per_page not in conf['ALLOWED_VALUES']:
        per_page = conf['PER_PAGE']

    request.session['per_page'] = per_page
    paginator = Paginator(obj_list, per_page, conf['ORPHANS'])

    try:
        page_obj = paginator.page(int(request.GET.get('page', default=1) or 1))
    except EmptyPage:
        raise Http404

    p_context = {
        'paginator': paginator,
        'page_obj': page_obj,
        'request': request,
    }
    p = paginate(p_context)
    p.update({'pagination_allowed_values': conf['ALLOWED_VALUES']})
    return p
