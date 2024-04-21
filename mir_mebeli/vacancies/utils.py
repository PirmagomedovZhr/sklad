# -*- coding: utf-8 -*-

from mir_mebeli.vacancies.models import Vacancy

def get_nodes(request):
    return list(Vacancy.objects.all())
