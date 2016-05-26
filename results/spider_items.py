# coding:utf-8
#Stage 2 Update (Python 3)
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from scrapy.contrib.djangoitem import DjangoItem
from dynamic_scraper.models import Scraper, SchedulerRuntime

from .models import Wuba, WubaNotmatch, Dianping, DianpingNotmatch, BaixingNotmatch, Baixing



# ---------------------------------------------------------------------------
# 以下爬虫相关
class CompanyItem(DjangoItem):
    # 统计用字段
    max_page = None  # 爬某一城市的最大页数
    this_page = None

    def __init__(self, *args, **kwargs):
        super(CompanyItem, self).__init__(*args, **kwargs)
        self.fields['max_page'] = self.max_page


class WubaItem(CompanyItem):
    django_model = Wuba


class WubaNotmatchItem(CompanyItem):
    django_model = WubaNotmatch


class DianpingItem(CompanyItem):
    django_model = Dianping


class DianpingNotmatchItem(CompanyItem):
    django_model = DianpingNotmatch


class BaixingItem(CompanyItem):
    django_model = Baixing


class BaixingNotmatchItem(CompanyItem):
    django_model = BaixingNotmatch
