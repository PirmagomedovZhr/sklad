# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404

from cms.utils import auto_render

from mir_mebeli.vacancies.models import Vacancy


@auto_render
def root(request):
    vacancies = Vacancy.objects.filter(close=False)
    return 'cms/pages/vacancies.html', {'vacancies': vacancies}


@auto_render
def vacancy(request, vacancy=None):
    vacancy = get_object_or_404(Vacancy, slug=vacancy, close=False)
    is_first_view = request.session.get('first_view_%s' % vacancy.pk, True)
    if is_first_view:
        vacancy.count_view += 1
        vacancy.save()
        request.session['first_view_%s' % vacancy.pk] = False
    return 'cms/pages/vacancy.html', {'vacancy': vacancy}
