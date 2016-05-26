# coding:utf-8
from django.db.utils import IntegrityError
from scrapy import log
from scrapy.exceptions import DropItem
from dynamic_scraper.models import SchedulerRuntime


from results.models import Wuba, WubaNotmatch, Baixing, BaixingNotmatch, Dianping, DianpingNotmatch
from results.spider_items import WubaItem, WubaNotmatchItem, BaixingItem, BaixingNotmatchItem, DianpingItem, DianpingNotmatchItem


def get_object_or_none_by_refurl(company, item):
    # ref url 不存在 返回 None
    # 有一个以上 返回第一个
    if 'ref_url' not in item:
        return False

    objs = company.objects.filter(ref_url=item['ref_url'])
    if objs.count() > 0:
        return objs[0]
    else:
        return None


def get_object_or_none_by_tel_title(company, item):
    # 当 tel title 不存在 返回 none
    # 有一个以上 返回第一个
    if 'tel' not in item and 'title' not in item:
        return None
    objs = company.objects.filter(tel=item['tel'], title=item['title'])
    if objs.count() > 0:
        return objs[0]
    else:
        return None


class MatchPipeline(object):
    # 将未匹配的分表
    def process_item(self, item, spider):
        if 'yt_first_cate_name' in item and item['yt_first_cate_name'] is not None and item['yt_first_cate_name'] != '':
            return item

        else:
            # 未匹配
            if type(item) == WubaItem:
                new_item = WubaNotmatchItem()
            if type(item) == BaixingItem:
                new_item = BaixingNotmatchItem()
            if type(item) == DianpingItem:
                new_item = DianpingNotmatchItem()

            for k in item:
                new_item[k] = item[k]
            return new_item


class DataCleanPipeline(object):
    # 脏数据清理
    def process_item(self, item, spider):
        # 去除空格 返回新的字段值
        def replace_space(item, field_name):
            if field_name not in item:
                return None
            else:
                return item[field_name].replace('\t', '').replace('\n', '').replace(' ', '')

        # 58 addr 空格
        if type(item) == WubaItem:
            item['addr1'] = replace_space(item, 'addr1')
            item['addr2'] = replace_space(item, 'addr2')
            item['address'] = replace_space(item, 'address')

        return item


class WubaItemPipeline(object):

    def process_item(self, item, spider):
        if type(item) in [WubaItem, WubaNotmatchItem]:
            if type(item) == WubaItem:
                wuba = get_object_or_none_by_refurl(Wuba, item)
            else:
                wuba = get_object_or_none_by_refurl(WubaNotmatch, item)
            try:
                if wuba is None:
                    # create one
                    item['yt_website'] = spider.ref_object
                    #item['count'] = 1
                    item.save()
                else:
                    wuba.count = wuba.count + 1
                    wuba.save()
            except Exception as e:
                spider.log(str(e), log.ERROR)
                raise DropItem("Missing attribute.")
        return item


class DianpingItemPipeline(object):

    def process_item(self, item, spider):
        if type(item) in [DianpingItem, DianpingNotmatchItem]:
            if type(item) == DianpingItem:
                dp = get_object_or_none_by_refurl(Dianping, item)
            else:
                dp = get_object_or_none_by_refurl(DianpingNotmatch, item)
            try:
                if dp is None:
                    # create one
                    item['yt_website'] = spider.ref_object
                    #item['count'] = 1
                    item.save()
                else:
                    dp.count = dp.count + 1
                    dp.save()
            except Exception as e:
                spider.log(str(e), log.ERROR)
                raise DropItem("Missing attribute.")
        return item


class BaixingItemPipeline(object):

    def process_item(self, item, spider):
        # 判断 tel title
        if type(item) in [BaixingItem, BaixingNotmatchItem]:
            if type(item) == BaixingItem:
                obj = get_object_or_none_by_tel_title(Baixing, item)
            else:
                obj = get_object_or_none_by_tel_title(BaixingNotmatch, item)
            try:
                if obj is None:
                    # create one
                    item['yt_website'] = spider.ref_object
                    #item['count'] = 1
                    item.save()
                else:
                    obj.count = obj.count + 1
                    obj.save()
            except Exception as e:
                spider.log(str(e), log.ERROR)
                raise DropItem("Missing attribute.")
        return item
