# coding:utf-8
import copy
import re
import logging
import urlparse
import datetime
import scrapy
from dynamic_scraper.spiders.django_spider import DjangoSpider

from results.models import Baixing
from results.spider_items import BaixingItem

from sources.models import Website
from sources.utils import get_max_page

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


def get_first(e):
    try:
        return e.extract()[0]
    except Exception:
        return None


def get_credit_url(item):
        if 'user_url' not in item:
            return None
        if item['user_url'] is None or item['user_url'].strip() == '':
            return None

        credit = 'http://www.baixing.com/credit/?uid=u'
        # person = 'http://www.baixing.com/u/72146402/'
        person = 'http://www.baixing.com/u/'
        # weidian = 'http://www.baixing.com/weishop/w54224800/'
        weidian = 'http://www.baixing.com/weishop/w'

        u_id = item['user_url'].replace(person, '').replace(weidian, '').replace('/', '')
        return credit + u_id


class BaixingGeneralSpider(DjangoSpider):
    name = 'baixing_general_spider'

    def __init__(self, *args, **kwargs):
        self._set_ref_object(Website, **kwargs)
        self.scraper = self.ref_object.scraper
        self.scrape_url = self.ref_object.url
        #self.scrape_urls = self.ref_object.urls  # yzy add
        self.scheduler_runtime = self.ref_object.scraper_runtime
        self.scraped_obj_class = Baixing
        self.scraped_obj_item_class = BaixingItem
        super(BaixingGeneralSpider, self).__init__(self, *args, **kwargs)


    def _set_start_urls(self, scrape_url):
        self.start_urls.append(scrape_url)
        self.pages = ["",]


    def parse(self, response):
    #def parse(self, response,  xs=None, from_page='MP'):
    #  此处在原链接基础上转到服务list
        xs = None
        from_page = 'MP'
        print(type(response))
        print response
        self._set_loader(response, from_page, xs, self.scraped_obj_item_class())
        item = self.loader.load_item()

        ul = response.css('#id-ul-baixing')
        for a_tag in ul.xpath("li/a"):
            company = copy.deepcopy(item)
            aa_name = get_first(a_tag.xpath('text()'))
            aa_href = get_first(a_tag.xpath('@href'))
            aa_id = get_first(a_tag.xpath('@data-id'))
            aa_factor = get_first(a_tag.xpath('@data-factor'))
            company['max_page'] = get_max_page(aa_factor)
            company['addr0'] = aa_name
            company['yt_city'] = aa_id
            if aa_href is not None:
                aa_href = urlparse.urljoin(aa_href, '/fuwu/')
            yield scrapy.Request(aa_href, meta={'company': company}, cookies={"rfb": "1"}, callback=self.parse_index_page)


    def parse_index_page(self, response):
        # 此处是 解析 http://shanghai.baixing.com/fuwu/?afo=ccF
        meta_company = response.meta['company']

        #response.xpath("//div[@class='items']").extract()[0]
        for a_tag in response.xpath("//div[@class='items']")[0].xpath("a")[0:3]:
            category_name = get_first(a_tag.xpath("text()"))
            category_url = get_first(a_tag.xpath("@href"))
            company = copy.deepcopy(meta_company)
            next_url = urlparse.urljoin(response.url, category_url)
            company['first_category'] = u'服务'
            company['second_category'] = category_name

            yield scrapy.Request(next_url, meta={'company': company}, cookies={"rfb": "1"}, callback=self.third_category)


    def third_category(self, response):
        #二级分类
        meta_company = response.meta['company']
        if len(response.xpath("//div[@class='items']"))==0:
            #分页
            print 'get not cate'
            print response.headers
            # f = open('test.txt','w+')
            # f.write(response.body)
            # f.close()
            # raise Exception
            for i in range(1, company['max_page']):
                next_page = '?page='+str(i)
                company = copy.deepcopy(meta_company)
                page_url = urlparse.urljoin(response.url, next_page)
            yield scrapy.Request(page_url, meta={'company': company}, callback=self.company_list)
        else:
            #二级根据h4的text判断类型
            for div_tag in response.css(".fieldset"):
                #div class=fieldset
                if get_first(div_tag.xpath("h4/text()")) == u'地区':
                    pass
                if get_first(div_tag.xpath("h4/text()")) == u'价格':
                    pass
                if get_first(div_tag.xpath("h4/text()")) == u'服务内容':
                    print 'get fuwu'
                    for a_tag in div_tag.xpath("div/a"):

                        company = copy.deepcopy(meta_company)
                        category_name = get_first(a_tag.xpath("text()"))
                        company['third_category'] = category_name
                        print category_name

                        if category_name != u'其他':
                            category_url  = get_first(a_tag.xpath("@href"))
                            next_url = urlparse.urljoin(response.url, category_url)
                            # 分页
                            for i in range(1, company['max_page']):
                                next_page = '?page='+str(i)
                                page_url = urlparse.urljoin(next_url, next_page)

                                yield scrapy.Request(page_url, meta={'company': company}, callback=self.company_list)


    def company_list(self,response):
        #在此for判断重复
        print 'in company_list'
        meta_company = response.meta['company']
       
        is_vip = False
        is_top = False

        def is_date_err(pdate, url):
            return False

        print len(response.css("#media"))
        #公司列表
        for li_tag in response.css("#media").xpath("li"):
            # 判断发布日期
            pub_date =  get_first(li_tag.xpath("div/div/small[@class='pull-right']/text()"))


            title = get_first(li_tag.xpath("div/div/a/text()"))
            #是否vip
            vip_class = get_first(li_tag.xpath("div/div/a/@data-original-title"))
            if vip_class == u'VIP\u4f1a\u5458':
                is_vip = True
            else:
                is_vip = False

            is_up_list = li_tag.xpath("div/div/small/a/text()").extract()
            if u'\u9876' in is_up_list:
                #顶
                is_top = True
            else:
                is_top = False

            url = get_first(li_tag.xpath("div/div/a/@href"))
            #已正确的url
            next_url = url
            # tel qq 
            profile = li_tag.xpath("//div[@class='pull-right fuwu-listing-typo-small-right']/a")
            tel = get_first(profile.xpath('@data-contact'))
            qq = get_first(profile.xpath('@data-qq'))

            company = copy.deepcopy(meta_company)
            company['qq'] = qq
            company['tel'] = tel
            company['title'] = title
            company['is_top'] = is_top
            company['is_vip'] = is_vip

            yield scrapy.Request(next_url, meta={'company': company}, callback=self.parse_detail)


    def parse_detail(self,response):
        company = response.meta['company']
        # print 'get length'
        # print response.url
        # print len(response.body)

        addr0 = None
        addr1 = None
        addr2 = None
        addr3 = None
        service = None
        name = None
        text = None

        #
        is_certified_company = False
        is_certified_person = False
        address = None
        weidian_introduction =None
        img_urls =None

        if 'tel' in company:
            tel = company['tel']
        else:
            tel = None

        if 'qq' in company:
            qq = company['qq']
        else:
            qq = None

        div = response.xpath("//div[@class='new-detail clearfix']")
        for span_tag in div.xpath("span"):
            label_tag_text = get_first(span_tag.xpath("label/text()"))

            if label_tag_text ==u"服务内容：":
                service = ",".join(span_tag.xpath("a/text()").extract())
            if label_tag_text ==u"公司名称：":
                name = get_first(span_tag.xpath("text()"))
            if label_tag_text ==u'QQ号：':
                pass
            if label_tag_text ==u'地区：':
                #多个地区，可能不存在
                #自定义地址
                addr3 = "".join(span_tag.xpath("span/text()").extract()).replace(u'\xa0','').replace('-','')

                addrs = span_tag.xpath("a/text()").extract()
                if len(addrs) == 3:
                    #2地区 加地图
                    #此时有自加地址
                    addr1 = span_tag.xpath("a/text()").extract()[0]
                    addr2 = span_tag.xpath("a/text()").extract()[1]

                if len(addrs) ==2:
                    #2diqu 或地区加地图
                    addr1 = span_tag.xpath("a/text()").extract()[0]
                    addr2 = span_tag.xpath("a/text()").extract()[1]
                    # 判断addr2 是否错误
                    if u'[\u5730\u56fe\u53ca\u4ea4\u901a]'==addr2:
                        addr2 = ''

                    #span_tag.xpath("a/text()").extract()
                if len(addrs)==1:
                    #1diqu
                    addr1 = span_tag.xpath("a/text()").extract()[0]  
                    #地图及交通
                    if addr1 == u'[\u5730\u56fe\u53ca\u4ea4\u901a]':
                        addr1 = ""



        #desc
        # typo-p textwrap
        if len(div.xpath("//div[@class='typo-p textwrap']").extract()) >0:
            texts = div.xpath("//div[@class='typo-p textwrap']/text()").extract()
            text = "".join(texts)
            text = text.replace(u'\u200b','').replace(u'\u200c','')

        div_imgs = response.xpath("//div[@class='img sep']")
        urls = []
        if len(div_imgs) != 0:
            for img in div_imgs.xpath("div/img/@src"):
                img_url = img.extract()
                urls.append(img_url)
        img_urls = ','.join(urls) #得到imgurls

        #
        verify_div = response.xpath("//div[@class='verify-body']")
        for a_tag in verify_div.xpath("a"):
            if get_first(a_tag.xpath("text()")) == u'\xa0\u8425\u4e1a\u6267\u7167' and get_first(a_tag.xpath("span/@style"))==u'color: #7ed31e;':
                #营业执照
                is_certified_company = True
            if get_first(a_tag.xpath("text()")) == u'\xa0\u8eab\u4efd\u8bc1' and get_first(a_tag.xpath("span/@style"))==u'color: #7ed31e;':
                is_certified_person = True
                #身份证

        #
        info_div = response.xpath("//div[@class='shop-info']")
        if len(info_div) != 0:
            #注意此处命名原网页有错
            address = get_first(info_div[0].xpath("div[@class='shop-desc']/div[@class='info-content']/text()"))
            weidian_introduction = get_first(info_div[0].xpath("div[@class='shop-address']/div[@class='info-content']/text()"))


        #正则
        qqs = None
        mails = None
        company_urls =None
        tels = None


        #re_telel2 = r'\d{3}-\d{8}|\d{4}-\d{7,8}|(13\d|14[57]|15[^4,\D]|17[678]|18\d)\d{8}|170[059]\d{7}'
        re_mobi = r'(?:13\d|14[57]|15[^4,\D]|17[678]|18\d)\d{8}|170[059]\d{7}'
        re_tel = r'0\d{2,3}-?\d{7,8}'
        re_qq = r'QQ(?::|：|\s{1,2})?\d+'
        #re_web = r'http://([a-zA-Z0-9/\.]*)|www\..*\.(?:com|net|com\.cn)(/[a-zA-Z0-9/]*)?'
        #re_web = r'[:a-zA-z/0-9\.]+\.(?:cn|net|com)(?:[/a-zA-Z0-9)]*)'
        re_web = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        #re_web = r'http://([a-zA-Z0-9/\.])*'
        #re_web2 = 'www\..*\.(com|net|com\.cn)(/[a-zA-Z0-9/]*)?'
        re_mail = r"[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?"
        
        
        if text != None and len(text) !=0:
            company_urls_list = map(str,re.findall(re_web,text))
            company_urls = ",".join(set(company_urls_list))
            mails_list = map(str,re.findall(re_mail,text))
            mails = ",".join(set(mails_list))


            #company_urls = ",".join(str(v) for v in re.findall(re_web,text))
            #mails        = ",".join(str(v) for v in re.findall(re_mail,text))
            qqs_list = []
            for r in re.findall(re_qq,text,re.IGNORECASE):
                rs = str(r).replace("q",'').replace('Q','').replace(':','').replace('：',"").replace(' ','')
                if qq != None and rs == qq:
                    pass
                else:
                    if len(rs)>=5:
                        qqs_list.append(rs)

            qqs = ",".join(set(qqs_list))

            tels_list = []
            for r in re.findall(re_tel,text):
                if tel != None and str(r) == tel:
                    pass
                else:
                    tels_list.append(str(r))
            for r in re.findall(re_mobi,text):
                if tel != None and str(r) == tel:
                    pass
                else:
                    tels_list.append(str(r))


            tels = ",".join(set(tels_list))


        #"info-content"
        company['name']=name
        
        # 首次发布时间 更新时间
        published_time_str = get_first(response.xpath("//span[@data-toggle='tooltip']/@title"))
        if published_time_str:
            pattern_time = re.compile(u"(\d+)年(\d+)月(\d+)日")
            res = re.findall(pattern_time, published_time_str)
            print res
            if len(res) > 0:
                try:
                    pdate = datetime.date(int(res[0][0]), int(res[0][1]), int(res[0][2]))
                    company['published_date'] = pdate
                except Exception as e:
                    print e
                    pass
        #update_time = get_first(response.xpath("//span[@data-toggle='tooltip']/@title"))

        company['addr1']=addr1
        company['addr2']=addr2
        company['addr3']=addr3
        company['service']=service
        company['desc']=text
        company['ref_url']=response.url

        company['company_urls']=company_urls
        company['is_certified_company']=is_certified_company
        company['is_certified_person']=is_certified_person
        company['address']=address
        company['weidian_introduction']=weidian_introduction
        company['img_urls']=img_urls
        company['mails']=mails
        company['additional_qqs']=qqs
        company['additional_tels']=tels
        # print text
        # print qq
        # print addr0
        # print addr1
        # print addr2
        # print addr3
        # print service
        # print tel

        #return company
        shop_topic = response.xpath("//div[@class='shop-topic']")
       # print shop_topic
       # print len(shop_topic)
        if len(shop_topic) == 1:
            shop_url = get_first(shop_topic.xpath("a/@href"))
            company['user_url'] = shop_url
            if shop_url is not None:
                yield scrapy.Request(shop_url,meta={'company':company},callback=self.detail_info)
            else:
                yield company
        else:
            company['user_url'] = get_first(response.xpath("//div[@class='user-info']/div[@class='media-body']/a/@href"))
            if company['user_url'] is not None:
                next_url = get_credit_url(company)
                yield scrapy.Request(next_url,meta={'company':company},callback=self.parse_credit)
            else:
                yield company


    def detail_info(self,response):
        print 'in deatil info'
        company = response.meta['company']

        lis = response.xpath("//div[@class='filter']/ul/li[@class='nav1']")
        detailed_category = ",".join(lis.xpath("a/text()").extract())

        shop_name = get_first(response.xpath("//div[@class='shop-name']/div/text()"))
        shop_desc = get_first(response.xpath("//div[@class='shop-desc']/text()"))
        shop_address = get_first(response.xpath("//div[@class='shop-address']/text()"))
        if shop_address != None:
            shop_address  = shop_address.replace(u'地址：','')
        shop_tel  = get_first(response.xpath("//div[@class='shop-phone']/span/text()"))

        company['detailed_category'] = detailed_category
        company['alt_name'] = shop_name
        company['info_tel'] = shop_tel
        if shop_desc != None and len(shop_desc) > 0:
            company['weidian_introduction'] = shop_desc
        

        if 'user_url' in company and company['user_url'] is not None:
                next_url = get_credit_url(company)
                yield scrapy.Request(next_url,meta={'company':company},callback=self.parse_credit)
        else:
            yield company

    def parse_credit(self, response):
        company = copy.deepcopy(response.meta['company'])

        is_certified_xinyong=False
        is_certified_person=False
        is_certified_company=False
        is_certified_weixin=False
        is_certified_weibo=False
        is_certified_email=False
        is_certified_tel=False
        company_name = None
        user_name = None
        user_date = None  # datetime
        pic_url = None

        mobile_addr = None

        user_date = get_first(response.xpath('//div[@class="user-info"]/span[2]/text()')) 

        # user_info_div = response.xpath('//div[@class="user-info"]')
        user_name = get_first(response.xpath('//*[@class="user-name"]/text()'))
        user_name_title = get_first(response.xpath('//*[@class="user-name"]/@title'))
        if user_name_title is not None and len(user_name_title) > 2:
            user_name = user_name_title

        pic_url = get_first(response.xpath('//*[@class="avatar-box"]/img/@src'))

        # company name
        company_name = get_first(response.xpath('//*[@class="tooLongName"]/text()'))
        company_name_title = get_first(response.xpath('//*[@class="tooLongName"]/@title'))
        if company_name_title is not None:
            if len(company_name_title) > 2:
                company_name = company_name_title

        # mobile addr
        mobile_addr_div = response.xpath('//div[@class="recent "]')  # 注意空格
        if mobile_addr_div is not None:
            if len(mobile_addr_div) > 0:
                desc_name = get_first(mobile_addr_div.xpath('div/text()'))
                if desc_name is not None:
                    if desc_name[0:4] == u'手机号码':
                        mobile_addr = get_first(mobile_addr_div.xpath('div[2]/span/text()'))


        for bind in response.xpath('//*[@class="bindname active"]'):
            name = get_first(bind.xpath('text()'))
            if name is None:
                continue

            if name == u'芝麻信用':
                is_certified_xinyong = True
            if name == u'身份证':
                is_certified_person = True
            if name == u'营业执照':
                is_certified_company = True
            if name[0:2] == u'微信':
                is_certified_weixin = True
            if name[0:2] == u'微博':
                is_certified_weibo = True
            if name == u'邮箱帐号':
                is_certified_email = True
            if name[0:2] == u'固定':
                is_certified_tel = True

        # data clean
        if user_date is not None:
            user_date = user_date.replace(u'注册','').strip().replace(u'年',',').replace(u'月',',').replace(u'日','')
            temp = user_date.split(',')
            try:
                dt = datetime.datetime(int(temp[0]), int(temp[1]), int(temp[2]))
                user_date = dt
            except Exception:
                user_date = None

        if company_name is not None:
            company_name = company_name.replace(u'公司名称：', '').strip()

        if pic_url == 'http://s.baixing.net/img/refashion/default_avatar.png':
            pic_url = None

        if mobile_addr is not None:
            mobile_addr = mobile_addr.strip()

        if user_name is not None:
            user_name = user_name.strip()

        company['is_certified_xinyong'] = is_certified_xinyong
        company['is_certified_person'] = is_certified_person
        company['is_certified_company'] = is_certified_company
        company['is_certified_weixin'] = is_certified_weixin
        company['is_certified_weibo'] = is_certified_weibo
        company['is_certified_email'] = is_certified_email
        company['is_certified_tel'] = is_certified_tel

        company['certified_company_name'] = company_name
        company['user_name'] = user_name
        company['user_join_date'] = user_date
        company['user_photo_url'] = pic_url
        company['mobile_addr'] = mobile_addr

        yield company
