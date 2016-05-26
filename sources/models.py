# coding:utf-8
#Stage 2 Update (Python 3)
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from scrapy.contrib.djangoitem import DjangoItem
from dynamic_scraper.models import Scraper, SchedulerRuntime

from locations.models import AdministrativeArea

@python_2_unicode_compatible
class Website(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(null=True, blank=True)
    #urls = models.TextField(null=True, blank=True)
    #city_names = models.CharField(null=True, blank=True, max_length=255)
    scraper = models.ForeignKey(Scraper, blank=True, null=True, on_delete=models.SET_NULL)
    scraper_runtime = models.ForeignKey(SchedulerRuntime, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


# class SpiderStatus(models.Model):
#     STATUS_CHOICES = (
#         (0, 'unknown'),
#         (3, 'pending'),
#         (5, 'running'),
#         (7, 'finished'),
#     )

#     project_name = models.CharField(null=True, blank=True, max_length=255)
#     spider_id = models.CharField(null=True, blank=True, max_length=255) # todo
#     name = models.CharField(null=True, blank=True, max_length=255)
#     version = models.CharField(null=True, blank=True, max_length=255)  # todo
#     status = models.SmallIntegerField(default=0, choices=STATUS_CHOICES)

#     start_time = models.CharField(null=True, blank=True, max_length=255)  # run finish 的开始时间
#     end_time = models.CharField(null=True, blank=True, max_length=255)    # 上次执行的结束时间
#     last_active_time = models.CharField(null=True, blank=True, max_length=255)  # 最后一次执行时间

#     add_time = models.DateTimeField(auto_now_add=True)
#     modified_time = models.DateTimeField(auto_now=True)
