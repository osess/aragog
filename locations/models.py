# -*- coding: utf-8 -*-
import datetime
import json

from django.core.urlresolvers import reverse

from django.db import models
from django.db.models.signals   import post_save
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
#from django.contrib.gis.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from categories.models import Category
#from apps.utils.util_slugify import *
#from apps.utils.slug import unique_slugify


from mptt.models import MPTTModel
from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
# class Category(models.Model):
#     #site = models.ForeignKey(Site, default=settings.SITE_ID)
#     name = models.CharField(_("Name"), max_length=200)
#     slug = models.SlugField(_("Slug"))
#     # private_icon
#     # public_icon

#     def __unicode__(self):
#         return self.name



class AreaProperty(models.Model):
    code       = models.CharField(max_length=3,blank=True,null=True,verbose_name=_("country_code"))
    population = models.IntegerField(blank=True,null=True,verbose_name=_("population"))
    area       = models.IntegerField(blank=True,null=True,verbose_name=_("area"))                    #面积
    currency   = models.CharField(max_length=3,blank=True,null=True,verbose_name=_("currency"))      #货币
    continent  = models.CharField(max_length=2,blank=True,null=True,verbose_name=_("continent"))     #洲
    capital    = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("capital"))     #首都
    tld        = models.CharField(max_length=5,blank=True,null=True,verbose_name=_("tld"))       #域名？
    yt_importance = models.SmallIntegerField(blank=True,null=True,default=1,verbose_name=_("yt importance")) #重要度，10最高
    
    is_municipalities = models.BooleanField(default=False,verbose_name=_("is municipalities"))  # 直辖市
    is_provincial_capital = models.BooleanField(default=False,verbose_name=_("is provincial capital"))  # 省会
    #Special Administrative Region 特别行政区
    is_special_administrative_region = models.BooleanField(default=False,verbose_name=_("is special administrative region"))
    zipcode = models.CharField(verbose_name=_("zipcode"), null=True, max_length=25)

    class Meta:
        ordering = ['-yt_importance']



#AdministrativeArea
class AdministrativeArea(MPTTModel):
    parent = TreeForeignKey('self',
        blank=True,
        null=True,
        related_name=_('children'),
        verbose_name=_('parent'))
    name          = models.CharField(max_length=50,verbose_name=_("name"))
    old_names     = models.CharField(blank=True, null=True,max_length=200,verbose_name=_("old names")) #历史名称，逗号区分
    slug          = models.CharField(max_length=255,verbose_name=_('slug'))
    description   = models.TextField(blank=True, null=True,verbose_name=_("description"))
    active        = models.BooleanField(default=True, verbose_name=_('active'))
    area_property = models.OneToOneField(AreaProperty,blank=True,null=True,verbose_name=_('area property'))
    abolished_date  = models.DateField(blank=True,null=True,verbose_name=_('abolished date'))
    is_county_level_city = models.BooleanField(default=False,verbose_name=_("is county level city")) # 是否县级市
    administrative_level = models.SmallIntegerField(null=True,blank=True,verbose_name=_('administrative level'))
    alternative_names =  models.CharField(max_length=255,verbose_name=_("alternative names")) # 别名 逗号分隔
    short_name    = models.CharField(max_length=50,verbose_name=_("short name"))

    # 以上为jimu中的字段
    # 以下添加爬虫相关
    factor = models.SmallIntegerField(default=0, )  # 此参数表明爬虫优先级
    wuba_url = models.CharField(max_length=255, blank=True, null=True)
    baixing_url = models.CharField(max_length=255, blank=True, null=True)
    dianping_url = models.CharField(max_length=255, blank=True, null=True)



    objects = models.Manager()
    tree = TreeManager()

    def __unicode__(self):
        return u'%s' % self.name

    class MPTTMeta:
        order_insertion_by=['area_property']

#-------------------------------------------------------------------------------
    # 返回完整的地址给地图，用于显示
    @property
    def get_full_name(self):
        ancestors = self.get_ancestors(include_self=True)
        fullname = ''
        for a in ancestors:
            fullname += a.name
        return fullname

#-------------------------------------------------------------------------------
    # 返回 aa 的完整 json 格式
    @property
    def to_full_json(self):
        level_map = {                    # level 对应的 名称
            0:'country',                 # 0 表示国家
            1:'province',                # 1 表示省
            2:'city',
            3:'district',
            4:'town',
        }
        d = {}
        d['level'] = self.level
        d['id'] = self.id
        d['name'] = self.name
        d['is_leaf_node'] = self.is_leaf_node()
        d['level_name'] = level_map.get(self.level)
        children_list = []
        for children_item in self.get_children():
            temp_dict = {}
            temp_dict['id'] = children_item.id
            temp_dict['level'] = children_item.level
            temp_dict['name'] = children_item.name
            temp_dict['is_leaf_node'] = children_item.is_leaf_node()
            temp_dict['level_name'] = level_map.get(children_item.level)
            children_list.append(temp_dict)
        d['children'] = children_list
        # 读取 所有上级 aa
        for level in range(0,self.level+1):
            temp_dict = {}
            ancestor = self.get_ancestors(include_self=True).get(level=level)
            temp_dict['id'] = ancestor.id
            temp_dict['level'] = ancestor.level
            temp_dict['name'] = ancestor.name
            temp_dict['is_leaf_node'] = ancestor.is_leaf_node()
            temp_dict['level_name'] = level_map.get(ancestor.level)
            # 读取同级的数据 : 即 parent 相同, level 相同
            siblings_aas = AdministrativeArea.objects.filter(parent=ancestor.parent,level=ancestor.level)
            siblings_list = []
            for aa in siblings_aas:
                temp2_dict = {}
                temp2_dict['id'] = aa.id
                temp2_dict['level'] = aa.level
                temp2_dict['name'] = aa.name
                temp2_dict['is_leaf_node'] = aa.is_leaf_node()
                temp2_dict['level_name'] = level_map.get(aa.level)
                siblings_list.append(temp2_dict)
            temp_dict['siblings'] = siblings_list

            d[level_map.get(ancestor.level)] = temp_dict

        return json.dumps(d)

#-------------------------------------------------------------------------------
    # 返回逗号分割的城市信息 ，eg  上海市,浦东新区
    @property
    def get_full_aa_name_with_comma(self):
        ancestors = self.get_ancestors(include_self=True).exclude(level=0)
        fullname = ''
        for a in ancestors:
            if a.area_property and a.area_property.is_municipalities and (a.level == 2):
                pass
            else:
                fullname = fullname + ',' + a.name
        return fullname.lstrip(',')
