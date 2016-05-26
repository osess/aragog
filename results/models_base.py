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
from sources.models import Website

@python_2_unicode_compatible
class CompanyBase(models.Model):
    # 原始数据 部分
    # 地址相关
    addr0 = models.CharField(null=True, blank=True, max_length=255)
    addr1 = models.CharField(null=True, blank=True, max_length=255)
    addr2 = models.CharField(null=True, blank=True, max_length=255)
    addr3 = models.CharField(null=True, blank=True, max_length=255)
    address = models.CharField(null=True, blank=True, max_length=255)

    # 分类相关
    detailed_category = models.CharField(null=True, blank=True, max_length=255)
    first_category = models.CharField(null=True, blank=True, max_length=255)
    second_category = models.CharField(null=True, blank=True, max_length=255)
    third_category = models.CharField(null=True, blank=True, max_length=255)

    # qq email tel 等 联系方式
    qq = models.CharField(null=True, blank=True, max_length=255)
    qq_link = models.CharField(null=True, blank=True, max_length=255)
    tel = models.CharField(null=True, blank=True, max_length=255)
    info_tel = models.CharField(null=True, blank=True, max_length=255)
    additional_qqs = models.CharField(null=True, blank=True, max_length=255)
    additional_tels = models.CharField(null=True, blank=True, max_length=255)
    mails = models.CharField(null=True, blank=True, max_length=255)

    # vip 等认证资质
    is_certified_company = models.BooleanField(default=False)
    is_certified_person = models.BooleanField(default=False)
    is_top = models.BooleanField(default=False)
    is_vip = models.BooleanField(default=False)
    is_certified_xinyong = models.BooleanField(default=False)
    is_certified_weixin = models.BooleanField(default=False)
    is_certified_weibo = models.BooleanField(default=False)
    is_certified_email = models.BooleanField(default=False)
    is_certified_tel = models.BooleanField(default=False)

    # 统计相关
    views_count = models.IntegerField(default=0)  # 浏览次数
    comments_count = models.IntegerField(default=0)  # 评论次数
    latest_updated_date = models.DateField(null=True, blank=True)

    count = models.IntegerField(default=1)  # 爬取到的次数
    published_date = models.DateField(null=True, blank=True)

    created_time = models.DateTimeField(auto_now_add=True, null=True)
    ref_url = models.CharField(null=True, blank=True, max_length=255)
    modified_time = models.DateTimeField(auto_now=True, null=True)
    is_synced = models.BooleanField(default=False)

    # 介绍信息
    desc = models.TextField(null=True, blank=True)
    weidian_introduction = models.TextField(null=True, blank=True)
    title = models.CharField(null=True, blank=True, max_length=255)
    img_urls = models.TextField(null=True, blank=True)

    # 公司用户 名字等个人信息
    alt_name = models.CharField(null=True, blank=True, max_length=255)  # 公司别名
    # 
    name = models.TextField(null=True, blank=True)
    user_name = models.CharField(null=True, blank=True, max_length=255)
    contact_person = models.CharField(null=True, blank=True, max_length=255)
    certified_company_name = models.CharField(null=True, blank=True, max_length=255)
    user_url = models.CharField(null=True, blank=True, max_length=255)
    user_photo_url = models.CharField(null=True, blank=True, max_length=255)
    company_urls = models.TextField(null=True, blank=True)
    user_join_date = models.DateTimeField(null=True)
    company_url = models.CharField(null=True, blank=True, max_length=255)

    # 其他信息
    service = models.CharField(null=True, blank=True, max_length=255)
    mobile_addr = models.CharField(null=True, blank=True, max_length=255)
    review_rating = models.FloatField(blank=True, default=0.0)
    credit_url = models.CharField(null=True, blank=True, max_length=255)
    avg_consumption = models.IntegerField(default=0)  # 人均消费
    properties = models.TextField(null=True, blank=True)  # 需解析的信息

    yt_website = models.ForeignKey(Website)
    checker_runtime = models.ForeignKey(SchedulerRuntime, blank=True, null=True, on_delete=models.SET_NULL)

    # 与 yt 分类 城市 相关
    yt_city = models.ForeignKey(AdministrativeArea, null=True, blank=True)
    yt_first_cate_name = models.CharField(null=True, blank=True, max_length=255)
    yt_second_cate_name = models.CharField(null=True, blank=True, max_length=255)
    yt_third_cate_name = models.CharField(null=True, blank=True, max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        abstract = True


class WubaBase(CompanyBase):
    class Meta:
        abstract = True


class BaixingBase(CompanyBase):
    class Meta:
        abstract = True


@python_2_unicode_compatible
class DianpingBase(CompanyBase):
    class Meta:
        abstract = True

    def __str__(self):
        if self.name is not None:
            return self.name
        else:
            return 'empty name'
