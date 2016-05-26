# coding:utf-8
from aragog.settings import CITY_MAX_PAGE


# 城市lv 与爬虫爬取 页面的数量关系
def get_max_page(factor):
    #
    try:
        factor = int(factor)
    except Exception as e:
        print e
        return 3 + 1

    if factor in CITY_MAX_PAGE:
        return CITY_MAX_PAGE[factor] + 1
    else:
        return 3 + 1
