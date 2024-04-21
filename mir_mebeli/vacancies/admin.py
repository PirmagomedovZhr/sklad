from django.contrib import admin
from mir_mebeli.vacancies.models import Vacancy

class VacancyAdmin(admin.ModelAdmin):
    list_display = ('position', 'slug')

admin.site.register(Vacancy, VacancyAdmin)
