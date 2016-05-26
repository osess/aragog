# coding:utf-8

# 将爬到的 城市 url 插入 db
# 
from locations.models import AdministrativeArea
from django.db.models import Q


def get_aa(city_name):
    try:
        cities = AA.objects.filter(Q(short_name=city_name)|Q(name=city_name))
    except Exception:
        return None

    if cities.count() == 0 or cities.count() > 1:
        return None
    else:
        return cities[0]
