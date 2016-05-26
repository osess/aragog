# coding:utf-8
#Stage 2 Update (Python 3)
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from scrapy.contrib.djangoitem import DjangoItem
from dynamic_scraper.models import Scraper, SchedulerRuntime

from .models_base import WubaBase, DianpingBase, BaixingBase


class WubaNotmatch(WubaBase):
    pass


class Wuba(WubaBase):
    pass


class Dianping(DianpingBase):
    pass


class DianpingNotmatch(DianpingBase):
    pass


class Baixing(BaixingBase):
    pass


class BaixingNotmatch(BaixingBase):
    pass
