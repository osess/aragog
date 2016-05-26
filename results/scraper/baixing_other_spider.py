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

from scrapy import log

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


def extract_first(self):
    try:
        return self.extract()[0]
    except Exception:
        return None

from scrapy.selector import SelectorList
SelectorList.extract_first = classmethod(extract_first)




def get_first(e):
    try:
        return e.extract()[0]
    except Exception:
        return None


class BaixingOtherSpider(DjangoSpider):
    name = 'baixing_other_spider'

    def __init__(self, *args, **kwargs):
        self._set_ref_object(Website, **kwargs)
        self.scraper = self.ref_object.scraper
        self.scrape_url = self.ref_object.url
        #self.scrape_urls = self.ref_object.urls  # yzy add
        self.scheduler_runtime = self.ref_object.scraper_runtime
        self.scraped_obj_class = Baixing
        self.scraped_obj_item_class = BaixingItem
        super(BaixingOtherSpider, self).__init__(self, *args, **kwargs)


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
                aa_href = aa_href
            yield scrapy.Request(aa_href, meta={'company': company}, cookies={"rfb": "1"}, callback=self.parse_other_index)


    # 以下移植 todo
    def parse_other_index(self,response):
        meta_company = response.meta['company']

        peixun_company = copy.deepcopy(meta_company)
        jianzhi_company = copy.deepcopy(meta_company)
        chongwu_company = copy.deepcopy(meta_company)
        qiche_company = copy.deepcopy(meta_company)

        jianzhi = response.xpath('//*[@id="glist"]/div[7]/h3[2]/a')
        jianzhi_url = get_first(jianzhi.xpath('@href'))
        jianzhi_url = urlparse.urljoin(response.url,jianzhi_url)
        print jianzhi_url
        jainzhi_name = get_first(jianzhi.xpath('text()'))
        jianzhi_company['first_category']=jainzhi_name
        yield scrapy.Request(jianzhi_url,meta={'company':jianzhi_company,},cookies={"rfb": "1"},callback=self.jianzhi_second)

        #宠物
        chongwu = response.xpath('//*[@id="glist"]/div[9]/h3[2]/a')
        chongwu_url = get_first(chongwu.xpath('@href'))
        chongwu_url = urlparse.urljoin(response.url,chongwu_url)
        chongwu_name = get_first(chongwu.xpath('text()'))
        chongwu_company['first_category']=chongwu_name
        yield scrapy.Request(chongwu_url,meta={'company':chongwu_company,},cookies={"rfb": "1"},callback=self.chongwu_second)


        #汽车
        qiche = response.xpath('//*[@id="glist"]/div[3]/h3/a')
        qiche_url = get_first(qiche.xpath('@href'))
        qiche_url = urlparse.urljoin(response.url,qiche_url)
        qiche_name = get_first(qiche.xpath('text()'))
        qiche_company['first_category']=qiche_name
        yield scrapy.Request(qiche_url,meta={'company':qiche_company,},cookies={"rfb": "1"},callback=self.qiche_second)

        
        peixun = response.xpath('//*[@id="glist"]/div[5]/h3[3]/a')
        peixun_url = get_first(peixun.xpath('@href'))
        peixun_url = urlparse.urljoin(response.url,peixun_url)
        peixun_name = get_first(peixun.xpath('text()'))
        print peixun_name
        #peixun_company['first_category']=peixun_name
        yield scrapy.Request(peixun_url,meta={'company':peixun_company,},cookies={"rfb": "1"},callback=self.peixun_first)


    def qiche_second(self,response):
        company = copy.deepcopy(response.meta['company'])
        logging.debug('in qiche')
        #first_cate = response.xpath("//*[@id='top-filters']/form/div[1]/h4/text()")) #兼职
        for div_tag in response.css(".fieldset"):
                #div class=fieldset
            if get_first(div_tag.xpath("h4/text()")) == u'车辆':
                for a_tag in div_tag.xpath("div/a"):
                    category_name = get_first(a_tag.xpath("text()"))
                    # 汽车用品
                    if category_name == u'拼车/顺风车' or category_name == u'过户/验车' or category_name == u'维修保养' or category_name == u'汽车配件' or category_name == u'汽车用品':
                        category_url  = get_first(a_tag.xpath("@href"))
                        next_url = urlparse.urljoin(response.url,category_url)
                        this_company = copy.deepcopy(company)
                        this_company['second_category']=category_name
                        #分页
                        for i in range(1, company['max_page']):
                            next_page = '?page='+str(i)
                            page_url = urlparse.urljoin(next_url, next_page)
                            yield scrapy.Request(page_url, meta={'company': this_company}, callback=self.qiche_company_list)



    def peixun_first(self,response):
        company = copy.deepcopy(response.meta['company'])
        #first_cate = response.xpath("//*[@id='top-filters']/form/div[1]/h4/text()")) #兼职
        for div_tag in response.css(".fieldset"):
                #div class=fieldset
            if get_first(div_tag.xpath("h4/text()")) == u'培训':
                logging.debug('get peixun lei')

                for a_tag in div_tag.xpath("div/a"):
                    category_name = get_first(a_tag.xpath("text()"))

                    # 
                    if category_name is not None:
                        this_company = copy.deepcopy(company)
                        category_url  = get_first(a_tag.xpath("@href"))
                        next_url = urlparse.urljoin(response.url,category_url)
                        this_company['first_category']=category_name
                        logging.debug(category_name)
                        logging.debug(next_url)

                        yield scrapy.Request(next_url,meta={'company':this_company,},callback=self.peixun_second)



    def peixun_second(self,response):
        company = copy.deepcopy(response.meta['company'])
        #first_cate = response.xpath("//*[@id='top-filters']/form/div[1]/h4/text()")) #兼职
        for div_tag in response.css(".fieldset"):
                #div class=fieldset
            if get_first(div_tag.xpath("h4/text()")) == u'培训类型':
                for a_tag in div_tag.xpath("div/a"):
                    category_name = get_first(a_tag.xpath("text()"))
                    # 
                    if category_name is not None and category_name != u'其他':
                        this_company = copy.deepcopy(company)
                        category_url  = get_first(a_tag.xpath("@href"))
                        next_url = urlparse.urljoin(response.url,category_url)
                        this_company['second_category']=category_name

                        logging.debug(category_name)
                        logging.debug(next_url)
                        #分页
                        for i in range(1, company['max_page']):
                            next_page = '?page='+str(i)
                            page_url = urlparse.urljoin(next_url, next_page)
                            yield scrapy.Request(page_url, meta={'company': this_company}, callback=self.peixun_company_list)
        








    def chongwu_second(self,response):
        company = copy.deepcopy(response.meta['company'])
        #first_cate = response.xpath("//*[@id='top-filters']/form/div[1]/h4/text()")) #兼职
        for div_tag in response.css(".fieldset"):
                #div class=fieldset
            if get_first(div_tag.xpath("h4/text()")) == u'宠物':
                for a_tag in div_tag.xpath("div/a"):
                    category_name = get_first(a_tag.xpath("text()"))
                    if category_name == u'宠物用品/食品' or category_name == u'宠物服务/配种':
                        category_url  = get_first(a_tag.xpath("@href"))
                        next_url = urlparse.urljoin(response.url,category_url)
                        this_company = copy.deepcopy(company)
                        this_company['second_category']=category_name
                        #分页
                        for i in range(1, company['max_page']):
                            next_page = '?page='+str(i)
                            page_url = urlparse.urljoin(next_url, next_page)
                            yield scrapy.Request(page_url, meta={'company': this_company}, callback=self.chongwu_company_list)












    def jianzhi_second(self,response):
        company = copy.deepcopy(response.meta['company'])
        print 'in jianzhi_second'
        log.msg('jianzhi_second', level=log.DEBUG)
        log.msg(response.css('.fieldset'), level=log.DEBUG)
        print response.css('.fieldset')
        #first_cate = response.xpath("//*[@id='top-filters']/form/div[1]/h4/text()")) #兼职
        for div_tag in response.css(".fieldset"):
                #div class=fieldset
            print get_first(div_tag.xpath("h4/text()"))
            if get_first(div_tag.xpath("h4/text()")) == u'兼职':
                log.msg('in jianzhi field', level=log.DEBUG)
                for a_tag in div_tag.xpath("div/a"):
                    category_name = get_first(a_tag.xpath("text()"))
                    if category_name != u'其他兼职':
                        this_company = copy.deepcopy(company)
                        category_url  = get_first(a_tag.xpath("@href"))
                        next_url = urlparse.urljoin(response.url,category_url)
                        this_company['second_category']=category_name
                        #分页
                        for i in range(1, company['max_page']):
                            next_page = '?page='+str(i)
                            page_url = urlparse.urljoin(next_url, next_page)
                            yield scrapy.Request(page_url, meta={'company': this_company}, callback=self.jianzhi_company_list)
        



    def peixun_company_list(self,response):
        company = copy.deepcopy(response.meta['company'])

        is_vip = False
        is_top = False

        #公司列表
        for li_tag in response.css("#media").xpath("li"):
            this_company = copy.deepcopy(company)
            title = get_first(li_tag.xpath("div/div/a/text()"))
            logging.debug(title)
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
            logging.debug(next_url)
            # tel qq 
            profile = li_tag.xpath("//div[@class='pull-right fuwu-listing-typo-small-right']/a")
            tel = get_first(profile.xpath('@data-contact'))
            qq = get_first(profile.xpath('@data-qq'))

            this_company['is_vip']=is_vip
            this_company['is_top']=is_top
            this_company['title']=title

            yield scrapy.Request(next_url,meta={'company':this_company,},callback=self.peixun_detail)












    def jianzhi_company_list(self,response):
        company = copy.deepcopy(response.meta['company'])

        is_vip = False
        is_top = False

        #公司列表
        for li_tag in response.css("#media").xpath("li"):
            this_company = copy.deepcopy(company)
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

            this_company['is_vip']=is_vip
            this_company['is_top']=is_top
            this_company['title']=title

            yield scrapy.Request(next_url,meta={'company':this_company,},callback=self.jianzhi_detail)


    def qiche_company_list(self,response):
        company = copy.deepcopy(response.meta['company'])

        is_vip = False
        is_top = False

        #公司列表
        for li_tag in response.css("#media").xpath("li"):
            this_company = copy.deepcopy(company)
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

            this_company['is_vip']=is_vip
            this_company['is_top']=is_top
            this_company['title']=title

            yield scrapy.Request(next_url,meta={'company':this_company,},callback=self.qiche_detail)









    def chongwu_company_list(self,response):
        company = copy.deepcopy(response.meta['company'])

        is_vip = False
        is_top = False

        #公司列表
        for li_tag in response.css("#media").xpath("li"):
            this_company = copy.deepcopy(company)
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
            # profile = li_tag.xpath("//div[@class='pull-right fuwu-listing-typo-small-right']/a")
            # tel = get_first(profile.xpath('@data-contact'))
            # qq = get_first(profile.xpath('@data-qq'))

            this_company['is_vip']=is_vip
            this_company['is_top']=is_top
            this_company['title']=title

            yield scrapy.Request(next_url,meta={'company':this_company,},callback=self.chongwu_detail)




    def chongwu_detail(self,response):
        company = copy.deepcopy(response.meta['company'])

        print response.url
        print len(response.body)

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
        qq = None
        tel = None

        #tel
        per_tel = get_first(response.css('#num').xpath('text()'))
        bac_tel = get_first(response.xpath('//div[@class="contact-actions"]/a/@data-contact'))
        if per_tel is not None and bac_tel is not None:
            tel = per_tel.replace('*','') + bac_tel






        div = response.xpath('//*[@id="metadata"]/div[2]') 
        for span_tag in div.xpath("span"):
            label_tag_text = get_first(span_tag.xpath("label/text()"))

            if label_tag_text ==u"分类：":
                service = " ".join(span_tag.xpath("a/text()").extract())
            if label_tag_text ==u"公司名称：":
                name = get_first(span_tag.xpath("text()"))
                # print 'company_name'
                # print name
            if label_tag_text ==u'QQ号：':
                a_href = get_first(span_tag.xpath("a/@href"))
                qq = a_href.replace('http://wpa.qq.com/msgrd?v=3&uin=','').replace('&site=qq&menu=yes','')
                pass
            if label_tag_text ==u'地区：':
                #多个地区，可能不存在
                #自定义地址
                addr3 = "".join(span_tag.xpath("span/text()").extract()).replace(u'\xa0','').replace('-','').replace(u'地区：','')

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
        if len(response.xpath("//div[@class='new-description']/div[@class='typo-p textwrap']").extract()) >0:
            texts = response.xpath("//div[@class='new-description']/div[@class='typo-p textwrap']/text()").extract()
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

        #



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
            if len(res) > 0:
                try:
                    pdate = datetime.date(int(res[0][0]), int(res[0][1]), int(res[0][2]))
                    company['published_date'] = pdate
                except Exception:
                    pass

        company['addr1']=addr1
        company['addr2']=addr2
        company['addr3']=addr3

        company['tel']=tel
        company['qq']=qq
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

        #return company
        shop_topic = response.xpath("//div[@class='shop-topic']")
       # print shop_topic
       # print len(shop_topic)
        if len(shop_topic) == 1:
            shop_url = get_first(shop_topic.xpath("a/@href"))
            company['user_url'] = shop_url
            yield scrapy.Request(shop_url,meta={'company':company},callback=self.jianzhi_detail_info)
        else:
            company['user_url'] = get_first(response.xpath("//div[@class='user-info']/div[@class='media-body']/a/@href"))
            yield company



    def peixun_detail(self,response):
        company = copy.deepcopy(response.meta['company'])

        print response.url
        print len(response.body)

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
        qq = None
        tel = None

        #tel
        per_tel = get_first(response.css('#num').xpath('text()'))
        bac_tel = get_first(response.xpath('//div[@class="contact-actions"]/a/@data-contact'))
        if per_tel is not None and bac_tel is not None:
            tel = per_tel.replace('*','') + bac_tel






        div = response.xpath('//*[@id="metadata"]') 
        for span_tag in div.xpath("span"):
            label_tag_text = get_first(span_tag.xpath("text()"))

            if label_tag_text[0:2] == u"培训":    #  u"培训类型：":
                service = " ".join(span_tag.xpath("a/text()").extract())
            if label_tag_text[0:2] == u"学校":              # u"学校名称：":
                name = get_first(span_tag.xpath("text()"))
                if name is not None and len(name)>5:
                    name = name[5:]
                # print 'company_name'
                # print name
            if label_tag_text ==u'QQ号：':
                a_href = get_first(span_tag.xpath("a/@href"))
                qq = a_href.replace('http://wpa.qq.com/msgrd?v=3&uin=','').replace('&site=qq&menu=yes','')
                pass
            if label_tag_text ==u'地区：':
                #多个地区，可能不存在
                #自定义地址
                addr3 = "".join(span_tag.xpath("span/text()").extract()).replace(u'\xa0','').replace('-','').replace(u'地区：','')

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
        if len(response.xpath("//div[@class='maincol']/div[@class='typo-p textwrap']").extract()) >0:
            texts = response.xpath("//div[@class='maincol']/div[@class='typo-p textwrap']/text()").extract()
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

        #



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
            try:
                pdate = datetime.date(int(res[0][0]), int(res[0][1]), int(res[0][2]))
                company['published_date'] = pdate
            except Exception:
                pass

        company['addr1']=addr1
        company['addr2']=addr2
        company['addr3']=addr3

        company['tel']=tel
        company['qq']=qq
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

        #return company
        shop_topic = response.xpath("//div[@class='shop-topic']")
       # print shop_topic
       # print len(shop_topic)
        if len(shop_topic) == 1:
            shop_url = get_first(shop_topic.xpath("a/@href"))
            company['user_url'] = shop_url
            yield scrapy.Request(shop_url,meta={'company':company},callback=self.jianzhi_detail_info)
        else:
            company['user_url'] = get_first(response.xpath("//div[@class='user-info']/div[@class='media-body']/a/@href"))
            yield company












    def qiche_detail(self,response):
        company = copy.deepcopy(response.meta['company'])

        print response.url
        print len(response.body)

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
        qq = None
        tel = None

        #tel
        per_tel = get_first(response.css('#num').xpath('text()'))
        bac_tel = get_first(response.xpath('//div[@class="contact-actions"]/a/@data-contact'))
        if per_tel is not None and bac_tel is not None:
            tel = per_tel.replace('*','') + bac_tel




        div = response.xpath('//*[@id="metadata"]/div[@class="new-detail clearfix"]') 
        for span_tag in div.xpath("span"):
            label_tag_text = get_first(span_tag.xpath("label/text()"))

            if label_tag_text ==u"类型：" or label_tag_text ==u"服务内容：" or label_tag_text ==u"分类：" :
                service = " ".join(span_tag.xpath("a/text()").extract())
            if label_tag_text ==u"公司名称：":
                name = get_first(span_tag.xpath("text()"))
                # print 'company_name'
                # print name
            if label_tag_text ==u'QQ号：':
                a_href = get_first(span_tag.xpath("a/@href"))
                qq = a_href.replace('http://wpa.qq.com/msgrd?v=3&uin=','').replace('&site=qq&menu=yes','')
                pass
            if label_tag_text ==u'地区：':
                #多个地区，可能不存在
                #自定义地址
                addr3 = "".join(span_tag.xpath("span/text()").extract()).replace(u'\xa0','').replace('-','').replace(u'地区：','')

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
        if len(response.xpath("//div[@class='new-description']/div[@class='typo-p textwrap']").extract()) >0:
            texts = response.xpath("//div[@class='new-description']/div[@class='typo-p textwrap']/text()").extract()
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

        #



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
            try:
                pdate = datetime.date(int(res[0][0]), int(res[0][1]), int(res[0][2]))
                company['published_date'] = pdate
            except Exception:
                pass

        company['addr1']=addr1
        company['addr2']=addr2
        company['addr3']=addr3

        company['tel']=tel
        company['qq']=qq
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

        #return company
        shop_topic = response.xpath("//div[@class='shop-topic']")
       # print shop_topic
       # print len(shop_topic)
        if len(shop_topic) == 1:
            shop_url = get_first(shop_topic.xpath("a/@href"))
            company['user_url'] = shop_url
            yield scrapy.Request(shop_url,meta={'company':company},callback=self.jianzhi_detail_info)
        else:
            company['user_url'] = get_first(response.xpath("//div[@class='user-info']/div[@class='media-body']/a/@href"))
            yield company








    def jianzhi_detail(self,response):
        company =  copy.deepcopy(response.meta['company'])

        print response.url
        print len(response.body)

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
        qq = None
        tel = None

        #tel
        per_tel = get_first(response.css('#num').xpath('text()'))
        bac_tel = get_first(response.xpath('//div[@class="contact-actions"]/a/@data-contact'))
        if per_tel is not None and bac_tel is not None:
            tel = per_tel.replace('*','') + bac_tel






        div = response.xpath('//*[@id="metadata"]/div[2]') 
        for span_tag in div.xpath("span"):
            label_tag_text = get_first(span_tag.xpath("span/text()"))

            if label_tag_text ==u"服务内容：":
                service = " ".join(span_tag.xpath("a/text()").extract())
            if label_tag_text ==u"公司名称：":
                name = get_first(span_tag.xpath("text()"))
                # print 'company_name'
                # print name
            if label_tag_text ==u'QQ号：':
                a_href = get_first(span_tag.xpath("a/@href"))
                qq = a_href.replace('http://wpa.qq.com/msgrd?v=3&uin=','').replace('&site=qq&menu=yes','')
                pass
            if label_tag_text ==u'地区：':
                #多个地区，可能不存在
                #自定义地址
                addr3 = "".join(span_tag.xpath("span/text()").extract()).replace(u'\xa0','').replace('-','').replace(u'地区：','')

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
        if len(response.xpath("//div[@class='maincol']/div[@class='typo-p textwrap']").extract()) >0:
            texts = response.xpath("//div[@class='maincol']/div[@class='typo-p textwrap']/text()").extract()
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

        #



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
            try:
                pdate = datetime.date(int(res[0][0]), int(res[0][1]), int(res[0][2]))
                company['published_date'] = pdate
            except Exception:
                pass

        company['addr1']=addr1
        company['addr2']=addr2
        company['addr3']=addr3

        company['tel']=tel
        company['qq']=qq
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

        #return company
        shop_topic = response.xpath("//div[@class='shop-topic']")
       # print shop_topic
       # print len(shop_topic)
        if len(shop_topic) == 1:
            shop_url = get_first(shop_topic.xpath("a/@href"))
            company['user_url'] = shop_url
            yield scrapy.Request(shop_url,meta={'company':company},callback=self.jianzhi_detail_info)
        else:
            company['user_url'] = get_first(response.xpath("//div[@class='user-info']/div[@class='media-body']/a/@href"))
            yield company


    def jianzhi_detail_info(self,response):
        print 'in deatil info'
        company = copy.deepcopy(response.meta['company'])

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
        
        yield company