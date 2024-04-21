# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
import mptt

# Create your models here.

class Vacancy(models.Model):
    GENDER_CHOICES = (
        ('M', u'Мужчина'),
        ('F', u'Женщина'),
    )   
    position = models.CharField(u"должность", max_length = 50)
    slug = models.SlugField(editable=False, blank=True, null=True)
    salary = models.CharField(u"оклад", max_length = 50)
    age = models.CharField(u"возраст", max_length = 30, blank=True, null=True)
    gender = models.CharField(u"пол", max_length = 1, choices = GENDER_CHOICES, blank=True, null=True)
    education = models.CharField(u"образование", max_length = 50)
    experience = models.CharField(u"опыт работы", max_length = 50)
    schedule = models.CharField(u"график работы", max_length = 50, blank=True, null=True)
    acting = models.TextField(u"основные обязанности", blank=True, null=True)
    skill = models.TextField(u"требования к кандидату", blank=True, null=True)
    contact = models.TextField(u"контактное лицо", blank=True, null=True)
    count_view = models.PositiveIntegerField(u"кол-во просмотров", default = 0, editable=False)
    close = models.BooleanField(u"вакансия закрыта", default = False)
    
    def __unicode__(self):
        return u"%s" % self.position
    
    def save(self):
        from pytils.translit import slugify
        self.slug = slugify(self.position)
        super(Vacancy, self).save()
    
    def get_parent(self):
      return None
    def set_parent(self, parent):
      pass

    parent = property(get_parent, set_parent)

    def get_parent_id(self):
      return None
    def set_parent_id(self, parent):
      pass

    parent_id = property(get_parent_id, set_parent_id)
    
    def get_menu_title(self):
        return self.position

    def get_absolute_url(self):
        return reverse('vacancy_view', kwargs={'vacancy':self.slug})
    
    class Meta:
        verbose_name = u"вакансия"
        verbose_name_plural = u"вакансии"
        
try:
    mptt.register(Vacancy)
except mptt.AlreadyRegistered:
    pass
