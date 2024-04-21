# -*- coding: utf-8 -*-
from django.db import models


class TeaserManager(models.Manager):
    def get_teasers(self):
        return self.filter(published=True).order_by('?')


class Teaser(models.Model):
    """Тизер."""
    name = models.CharField(u'название', max_length=50)
    image = models.ImageField(u'картинка', upload_to='teasers/')
    link = models.URLField(u'ссылка', max_length=255, blank=True, default='')

    new = models.BooleanField(u'новинка', default=False)
    published = models.BooleanField(u'опубликован?', default=True)

    objects = TeaserManager()
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        verbose_name = u'тизер'
        verbose_name_plural = u'тизеры'
