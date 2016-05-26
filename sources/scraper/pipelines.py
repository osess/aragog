# coding:utf-8
from django.db.utils import IntegrityError
from scrapy import log
from scrapy.exceptions import DropItem
from dynamic_scraper.models import SchedulerRuntime

from locations.models import AdministrativeArea
from results.models import Wuba, Dianping, Baixing
from results.spider_items import WubaItem, BaixingItem, DianpingItem
from sources.category_match import get_category_by_dianping, get_category_by_wuba, get_category_by_baixing

class CategoryValitionPipeline(object):
    # 检测 分类是否在匹配中
    
    def process_item(self, item, spider):
        cate_fun = None
        matched = False
        res = None

        if type(item) == WubaItem:
            cate_fun = get_category_by_wuba
        if type(item) == DianpingItem:
            cate_fun = get_category_by_dianping

        if type(item) == BaixingItem:
            cate_fun = get_category_by_baixing

        if cate_fun is not None:
            first_category = None
            second_category = None
            third_category = None
            if 'first_category' in item:
                first_category = item['first_category']
            if 'second_category' in item:
                second_category = item['second_category']
            if 'third_category' in item:
                third_category = item['third_category']

            res = cate_fun(first_category, second_category, third_category)
            if res[0] is not None and res[0] != '':
                matched = True

        if matched:
            item['yt_first_cate_name'] = res[0]
            item['yt_second_cate_name'] = res[1]
            item['yt_third_cate_name'] = res[2]

            return item
        else:
            pass
            # todo
            # drop item

        return item


class CityPipeline(object):
    def process_item(self, item, spider):
        if item['yt_city'] is not None:
            city_id = item['yt_city']
            try:
                city = AdministrativeArea.objects.get(id=city_id)
                item['yt_city'] = city
            except Exception, e:
                spider.log(str(e), log.ERROR)
                item['yt_city'] = None

        return item
