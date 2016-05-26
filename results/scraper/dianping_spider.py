# coding:utf-8
import copy
import re
import logging
import urlparse
import scrapy
from dynamic_scraper.spiders.django_spider import DjangoSpider

from results.models import Dianping
from results.spider_items import DianpingItem
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


class DianpingGeneralSpider(DjangoSpider):
    name = 'dianping_general_spider'
    download_delay = 5

    def __init__(self, *args, **kwargs):
        self._set_ref_object(Website, **kwargs)
        self.scraper = self.ref_object.scraper
        self.scrape_url = self.ref_object.url
        #self.scrape_urls = self.ref_object.urls  # yzy add
        self.scheduler_runtime = self.ref_object.scraper_runtime
        self.scraped_obj_class = Dianping
        self.scraped_obj_item_class = DianpingItem
        super(DianpingGeneralSpider, self).__init__(self, *args, **kwargs)

    def _set_start_urls(self, scrape_url):

        self.start_urls.append(scrape_url)
        self.pages = ["",]

    def parse(self, response):
    #def parse(self, response,  xs=None, from_page='MP'):
        xs = None
        from_page = 'MP'
        print(type(response))
        print response
        self._set_loader(response, from_page, xs, self.scraped_obj_item_class())
        item = self.loader.load_item()

        ul = response.css('#id-ul-dianping')
        for a_tag in ul.xpath("li/a"):
            company = copy.deepcopy(item)
            aa_name = get_first(a_tag.xpath('text()'))
            aa_href = get_first(a_tag.xpath('@href'))
            aa_id = get_first(a_tag.xpath('@data-id'))
            company['addr0'] = aa_name
            company['yt_city'] = aa_id
            aa_factor = get_first(a_tag.xpath('@data-factor'))
            company['max_page'] = get_max_page(aa_factor)
            print aa_name
            print aa_href
            yield scrapy.Request(aa_href, meta={'company': company}, callback=self.parse_index_page)

    def parse_index_page(self, response):
        print response
        print 'rr'
        meta_company = copy.deepcopy(response.meta['company'])

        index_ul = response.css("#index-nav")    

        #休闲娱乐
        xiuxian_li = index_ul.xpath("li[@data-key='30']")
        #丽人
        liren_li = index_ul.xpath("li[@data-key='50']")
        #运动
        yundong_li = index_ul.xpath("li[@data-key='45']")
        #培训
        peixun_li = index_ul.xpath("li[@data-key='75']")
        #生活
        shenghuo_li = index_ul.xpath("li[@data-key='80']")
        #家装
        jiazhuang_li = index_ul.xpath("li[@data-key='90']")
        #汽车
        qiche_li = index_ul.xpath("li[@data-key='65']")

        # 结婚
        date_li = index_ul.xpath("li[@data-key='55']")
        # 医疗
        yiliao_li = index_ul.xpath("li[@data-key='85']")
        # 宠物
        chongwu_li = index_ul.xpath("li[@data-key='95']")
        # 亲子
        qinzi_li = index_ul.xpath("li[@data-key='70']")


        all_li = index_ul.xpath(
            "li[@data-key='30'] |li[@data-key='50'] | li[@data-key='45'] | li[@data-key='75'] | li[@data-key='80'] | li[@data-key='55'] | li[@data-key='85'] | li[@data-key='95']| li[@data-key= '70']| li[@data-key='65']| li[@data-key='90']")

        for li_tag in all_li:
            #休闲娱乐 其他为包含
            first_category = get_first(li_tag.xpath("a[@class='name']/span/text()"))

            for a_tag in li_tag.xpath("div/a[not(@item)]"):
                a_name = get_first(a_tag.xpath("text()"))  # sec_category
                a_href = get_first(a_tag.xpath("@href"))  # /beijing/life  /search
                next_url = urlparse.urljoin(response.url, a_href)
                if len(a_name) > 0 and a_name[-2:] != u'频道' and a_name[0:2] != u'更多':  # ???
                    company = copy.deepcopy(meta_company)
                    company['first_category'] = first_category
                    company['second_category'] = a_name
                    #此处错误
                    #company['city']=response.url

                    yield scrapy.Request(next_url, meta={'company': company}, callback=self.parse_quxian)


    def parse_quxian(self, response):
        company = copy.deepcopy(response.meta['company'])
        #地区

        div_tag = response.css("#region-nav")

        for a_tag in div_tag.xpath("a"):
            xian_name = get_first(a_tag.xpath("span/text()"))
            a_href = get_first(a_tag.xpath("@href"))
            this_company = copy.deepcopy(company)
            this_company['addr1'] = xian_name
            next_url = urlparse.urljoin(response.url, a_href)
            yield scrapy.Request(next_url, meta={'company': this_company}, callback=self.parse_street)


    def parse_street(self, response):

        company = copy.deepcopy(response.meta['company'])

        # 貌似街道
        div_tag = response.css("#region-nav-sub")

        for a_tag in div_tag.xpath("a[not(@class)]"):
            street_name = get_first(a_tag.xpath("span/text()"))
            a_href = get_first(a_tag.xpath("@href"))
            this_company = copy.deepcopy(company)
            this_company['addr2'] = street_name
            next_url = urlparse.urljoin(response.url, a_href)
            yield scrapy.Request(next_url, meta={'company': this_company}, callback=self.parse_list)


    # drop
    # todo
    def parse_page(self,response):

        # 分页处理 未写
        company = copy.deepcopy(response.meta['company'])
        next_url = response.url

        yield scrapy.Request(next_url,meta={'company':company},callback=self.parse_list)


    def parse_list(self, response):

        company = copy.deepcopy(response.meta['company'])
        shop_list = response.css("#shop-all-list").xpath("ul/li")


        for li_tag in shop_list:
            if len(li_tag.xpath("@data-midas")) == 1:
                #推广 # 注意对分页的影响
                pass
            else:
                pass

            a_href = get_first(li_tag.xpath("div[@class='txt']/div/a/@href"))
            next_url = urlparse.urljoin(response.url, a_href)
            this_company = copy.deepcopy(company)

            yield scrapy.Request(next_url, meta={'company': this_company}, callback=self.parse_detail)

        #分页处理
        div_page = response.xpath("//div[@class='page']")
        for a_tag in div_page.xpath('a'):
            if a_tag.xpath('text()') == u'下一页' and company['max_page'] > 0:
                a_href = get_first(a_tag.xpath('@href'))
                next_url = urlparse.urljoin(response.url, a_href)
                this_company = copy.deepcopy(company)
                this_company['max_page'] = this_company['max_page'] - 1
                yield scrapy.Request(next_url, meta={'company': this_company}, callback=self.parse_list)



    def parse_detail(self,response):
        company = copy.deepcopy(response.meta['company'])
        #company = DianpingItem()
        ref_url = response.url

        is_vip = False

        name = get_first(response.xpath("//h1[@class='shop-name']/text()"))
        if name is None:
            name = get_first(response.xpath("//div[@class='shop-name']/h1/text()"))
        if name is not None:
            name = name.replace(u'\n','').strip()

        str_addr = response.xpath("//div[@itemprop='street-address']")

        #xian = str_addr.xpath("a/span/text()").extract_first()
        address = get_first(str_addr.xpath("span/@title"))

        tel_texts = response.xpath("//span[@itemprop='tel']/text()").extract()
        tel = ",".join(tel_texts)

        vip_a = response.xpath("//a[@class='icon v-shop']")
        if len(vip_a) == 1:
            is_vip = True


        level = get_first(response.xpath("//div[@class='brief-info']/span/@title"))
        if level == None:
            level = ''

        company['is_vip'] = is_vip
        company['name'] = name
        company['addr3'] = address
        company['tel'] = tel
        company['ref_url'] = ref_url
        #company['level'] = level
        shop_time = ''

        #print response.xpath("//div[@class='other J-other Hide']/p/span[@class='info-name']/text()").extract_first()
        for p_tag in response.xpath("//div[@class='other J-other Hide']/p"):
            if get_first(p_tag.xpath("span[@class='info-name']/text()")) == u'\u522b\xa0\xa0\xa0\xa0\xa0\xa0\xa0\u540d\uff1a':
                company['title'] = get_first(p_tag.xpath("span[@class='item']/text()"))
            if get_first(p_tag.xpath("span[@class='info-name']/text()")) == u'营业时间：':
                shop_time = get_first(p_tag.xpath("span[@class='item']/text()")).strip()
            if get_first(p_tag.xpath("span[@class='info-name']/text()")) == u'商户简介：':
                desc_str = get_first(p_tag.xpath("text()"))
                if desc_str is not None:
                    company['desc'] = desc_str.replace('\n', '').replace('\t', '').replace(' ', '')


        #if response.xpath("//div[@class='other J-other Hide']/p/span[@class='info-name']/text()").extract_first() == u'\u522b\xa0\xa0\xa0\xa0\xa0\xa0\xa0\u540d\uff1a':
        #    company['another_name'] = response.xpath("//div[@class='other J-other Hide']/p/span[@class='item']/text()").extract_first()


        brief_list = response.xpath("//div[@class='brief-info']/span[@class='item']/text()").extract()
        if shop_time is not None and len(shop_time)>0:
            company['properties'] = ','.join(brief_list) + u',营业时间:'+ shop_time + level
        else:
            company['properties'] = ','.join(brief_list) + level
        
        company['addr0'] = get_first(response.xpath("//*[@id='page-header']/div/a[@class='city J-city']/text()"))

        # review rating
        review_span_class = get_first(response.xpath('//div[@class="brief-info"]/span[@title]/@class'))
        if review_span_class is not None:
            try:
                company['review_rating'] = int(review_span_class.replace('mid-rank-stars mid-str', ''))/10.0
            except Exception:
                pass

        # 人均消费 评论数
        brief_span = response.xpath('//div[@class="brief-info"]/span')
        for span in brief_span:
            span_str = get_first(span.xpath('text()'))
            if span_str is not None:
                if u'消费' in span_str or u'人均' in span_str:
                    cost = span_str.replace(u'消费：', '').replace(u'人均：', '').replace(u'元', '')
                    try:
                        company['avg_consumption'] = int(cost)
                    except Exception:
                        pass

                if u'评论' in span_str:
                    comment_count_str = span_str.replace('评论', '').replace('条', '')
                    try:
                        company['comments_count'] = int(comment_count_str)
                    except Exception:
                        pass

        a_url = get_first(response.xpath("//div[@id='aside']/div/div[@class='photos']/a/@href"))

        if a_url is None:
            yield company
        else:
            next_url = urlparse.urljoin(response.url, a_url)
            yield scrapy.Request(next_url, meta={'company': company}, callback=self.parse_img)


    def parse_img(self,response):
        company = copy.deepcopy(response.meta['company'])
        ul_tag = response.xpath("//div[@class='picture-list']/ul")

        img_list = []

        for li_tag in ul_tag.xpath('li'):
            img_url = get_first(li_tag.xpath('div/a/img/@src'))
            img_list.append(img_url)

        company['img_urls'] = ','.join(img_list)

        yield company
