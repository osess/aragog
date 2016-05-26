# coding:utf-8
import os, sys

# Setup environ
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../..'))

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aragog.settings")
django.setup()

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.db.models import F
from locations.models import AdministrativeArea


def set_sheng_hui(factor):

    aa = AdministrativeArea.objects.filter(level=2, area_property__is_provincial_capital=True)
    aa.update(factor=factor)
    print 'set_sheng_hui ok'


def set_zhixia(factor):
    aa = AdministrativeArea.objects.filter(level=2, area_property__is_municipalities=True)
    aa.update(factor=factor)
    print 'set_zhixia ok'


def set_as_yt_importance():
    # 设置 level 2 ,3 的aa 的factor 与yt_importance 相同
    aa = AdministrativeArea.objects.filter(level__in=[2, 3])
    for a in aa:
        factor = a.area_property.yt_importance
        a.factor = factor
        a.save()
    #aa.update(factor=F('area_property__yt_importance'))
    print 'set_as_yt_importance ok'

def set_factor():
    # 为不同的城市设置factor 用来计算爬虫爬行的页数
    print 'start ...'
    set_as_yt_importance()
    set_sheng_hui(10)
    set_zhixia(10)


if __name__ == '__main__':
    set_factor()
