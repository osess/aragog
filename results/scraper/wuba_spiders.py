#coding:utf-8
import copy
import re
import logging
import urlparse
import datetime
import scrapy
from dynamic_scraper.spiders.django_spider import DjangoSpider

from results.models import Wuba
from results.spider_items import WubaItem
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


def right_date(month, day):
    return True


class WubaGeneralSpider(DjangoSpider):
    name = 'wuba_general_spider'

    def __init__(self, *args, **kwargs):
        self._set_ref_object(Website, **kwargs)
        self.scraper = self.ref_object.scraper
        self.scrape_url = self.ref_object.url
        #self.scrape_urls = self.ref_object.urls  # yzy add
        self.scheduler_runtime = self.ref_object.scraper_runtime
        self.scraped_obj_class = Wuba
        self.scraped_obj_item_class = WubaItem
        super(WubaGeneralSpider, self).__init__(self, *args, **kwargs)

    # def get_url_dict(self):
    #     # 得到url 与 城市的字典
    #     if self.scrape_url is not null and self.scrape_url != '':
    #         if self.city_


    #     urls = self.scrape_urls.split(',')

    #def parse(self, response):
    def _set_start_urls(self, scrape_url):
        # 传入 scrape_url 参数无用
        # if self.scrape_url is not null and self.scrape_url != '':
        #     self.start_urls.append(self.scrape_url)
        # if self.scrape_urls is not null and self.scrape_urls != '':
        #     urls = self.scrape_urls.split(',')
        #     for u in urls:
        #         self.start_urls.append(u)

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

        ul = response.css('#id-ul-wuba')
        print ul
        for a_tag in ul.xpath("li/a"):
            company = copy.deepcopy(item)
            aa_name = get_first(a_tag.xpath('text()'))
            aa_href = get_first(a_tag.xpath('@href'))
            aa_id = get_first(a_tag.xpath('@data-id'))
            aa_factor = get_first(a_tag.xpath('@data-factor'))

            company['addr0'] = aa_name
            company['yt_city'] = aa_id
            company['max_page'] = get_max_page(aa_factor)
            if aa_href is not None:
                aa_href = urlparse.urljoin(aa_href, "/huangye/")
            yield scrapy.Request(aa_href, meta={'company': company}, callback=self.parse_index_page)


    def parse_index_page(self, response):
        meta_company = copy.deepcopy(response.meta['company'])

        main_div = response.xpath('//div[@class="main"]')
        #logging.debug(main_div)
        test = main_div.xpath('div[@class="box_cont"]/div/h5/a')
        #logging.debug(len(test))
        pattern1 = re.compile(r"http://(\w{1,10})\.58\.com")
        for a_tag in main_div.xpath('div[@class="box_cont"]/div/h5/a'):
            a_href = get_first(a_tag.xpath('@href'))
            first_category = get_first(a_tag.xpath('text()'))
            logging.debug(first_category)
            if a_href and first_category not in [u'招商加盟', u'公共服务', u'医疗健康']:
                company = copy.deepcopy(meta_company)
                company['first_category'] = first_category
                addr_names = re.findall(pattern1, response.url)
                if len(addr_names)>0:
                    addr = addr_names[0]
                    pass
                    # if addr in self.web_site.keys():
                        
                    #     company['addr0'] = self.web_site[addr]

                next_url = urlparse.urljoin(response.url, a_href)
                yield scrapy.Request(next_url, meta={'company': company}, callback=self.parse_second_category)


    def parse_second_category(self, response):
        company = copy.deepcopy(response.meta['company'])
        # a/following-sibling::*[1]
        all_h2 = response.xpath('//div[contains(@class, "cb")]/div/h2')
        logging.debug(len(all_h2))
        for h2_tag in all_h2:
            second_category = ''.join(h2_tag.xpath('a/text()').extract())
            logging.debug(second_category)
            a_href = get_first(h2_tag.xpath('a/@href'))
            next_url = a_href
            temp_company = copy.deepcopy(company)
            temp_company['second_category'] = second_category
            if temp_company['first_category'] == u'农林牧副渔':
                yield scrapy.Request(next_url, meta={'company': temp_company}, callback=self.noye_company_list)
            else:

                yield scrapy.Request(next_url, meta={'company': temp_company}, callback=self.parse_company_list)
                pass

    def parse_company_list(self, response):
        company = copy.deepcopy(response.meta['company'])
        table = response.css("#infolist").xpath('table')
        trs = table.xpath('tr')
        #logging.debug(table)
        #logging.debug(trs)
        logging.debug(len(trs))
        pattern2 = re.compile(r"\((\d{1,2})-(\d{1,2})\)")
        month = None
        day = None

        for tr in trs:
            temp_company = copy.deepcopy(company)
            div_t_tag = tr.xpath('td/div[@class="tdiv"]')
            if div_t_tag is None or len(div_t_tag) == 0:
                div_t_tag = tr.xpath('td')

            a_href = get_first(div_t_tag.xpath('a/@href'))
            #next_url = urlparse.urljoin(response.url, a_href)
            next_url = a_href
            is_best = get_first(div_t_tag.xpath('span[@class="jingpin"]'))
            is_top = get_first(div_t_tag.xpath('span[@class="ico ding"]'))

            if is_best is not None and is_best != '':
                pass
                # todo
                #temp_company['is_best'] = True
            if is_top is not None and is_top != '':
                temp_company['is_top'] = True

            # 分页测试
            div_text = ''.join(div_t_tag.xpath('text()').extract())
            date_res = re.findall(pattern2,div_text)
            if len(date_res) > 0:
                month = date_res[0][0]
                day = date_res[0][1]

            yield scrapy.Request(next_url, meta={'company': temp_company}, callback=self.parse_addr_company_detail)

        next_a_tag = response.xpath('//div[@class="pager"]/a[@class="next"]')
        if company['max_page'] > 0:
            if right_date(month, day):
                next_company = copy.deepcopy(company)
                next_company['max_page'] = next_company['max_page'] - 1 
                next_page_href = get_first(next_a_tag.xpath('@href'))
                next_page_url = urlparse.urljoin(response.url, next_page_href)
                yield scrapy.Request(next_page_url, meta={'company': next_company}, callback=self.parse_company_list)


    def parse_addr_company_detail(self, response):
        company = copy.deepcopy(response.meta['company'])
        company['ref_url'] = response.url
        logging.debug(response.url)
        company['tel'] = ''

        next_url = None
        # title
        main_title_div = response.xpath('//div[@class="mainTitle"]')
        title = get_first(main_title_div.xpath('h1/text()'))
        company['title'] = title
        # publish time
        index_show_div = response.css('#index_show')
        published_time = get_first(index_show_div.xpath('ul/li[@class="time"]/text()'))
        try:
            pub_timelist = published_time.split('-')
            company['published_date'] = datetime.date(int(pub_timelist[0]), int(pub_timelist[1]), int(pub_timelist[2]))
        except Exception:
            pass

        sumary_ul = response.xpath('//div[contains(@class, "col_sub sumary")]/ul')

        for li_tag in sumary_ul.xpath('li'):
            su_tit = get_first(li_tag.xpath('div[@class="su_tit"]/text()'))
            if su_tit is not None:
                su_tit = su_tit.replace(u'\xa0','').replace(u' ','').strip()
            cona = li_tag.xpath('div[contains(@class, "cona")]')
            if su_tit == u'服务区域':
                pass
            if su_tit == u'类别':
                third_category = get_first(li_tag.xpath('div/a/text()'))
                company['third_category'] = third_category
            if su_tit == u'咨询商家':
                su_con = li_tag.xpath('div[@class="su_con"]')
                tel = get_first(su_con.xpath('span[@class="l_phone"]/text()'))
                company['tel'] = tel
                guishu = get_first(su_con.xpath('span[@class="gsd"]/text()'))
                if guishu is not None:
                    guishu = guishu.replace(u'（', '').replace(u'归属地：', '').replace(u'）', '')
                    guishu = guishu.strip()
                    company['mobile_addr'] = guishu
            if su_tit == u'联系人':
                #print '联系人'
                user_name = get_first(li_tag.xpath('div/a/text()'))
                if user_name is not None:
                    user_name = user_name.strip()
                company['contact_person'] = user_name

        # 格式问题 thirdcategory maybe not get
        if  'third_category' not in company.keys() or company['third_category'] is None or company['third_category'] == '':
            for li_tag in sumary_ul.xpath('li/div/ul/li'):
                li_name = get_first(li_tag.xpath('i/nobr/text()'))
                if li_name is not None:
                    li_name = li_name.replace(u'\xa0','').replace(u' ','').strip()
                if li_name == '类别':
                    company['third_category'] = get_first(li_tag.xpath('div/a/text()'))



        # 详情
        detail_div = response.css('#con_1')
        newinfo_div = detail_div.xpath("div/div[@class='newinfo']")
        # addr
        for li_tag in newinfo_div.xpath('ul/li'):
            i_name =  get_first(li_tag.xpath('i/nobr/text()'))
            aas =  li_tag.xpath('a')
            if len(aas) > 0:
                addr1 =get_first(aas[0].xpath('text()'))
                company['addr1'] = addr1
            if len(aas) > 1:
                addr2 =get_first(aas[1].xpath('text()'))
                company['addr2'] = addr2
            if li_tag.xpath('text()').extract() is not None:
                addr3 = li_tag.xpath('text()').extract()
                #print 'addr3'
                #print addr3
                if addr3 is not None:
                    addr3 = ''.join(addr3).replace('-', '').replace('\n', '').replace('\t', '').strip()
                    company['addr3'] = addr3
            # pass

        # desc
        sub_1_div = response.css('#sub_1')
        desc1 = sub_1_div.xpath('div/article//text()').extract()
        desc = None
        if desc1 is not None:
            desc = ''.join(desc1).replace('-', '').replace('\n', '').replace('\t', '').strip()
            company['desc'] = desc

        # img
        img_div = response.css('#img_player1')
        img_urls = img_div.xpath('img/@src').extract()
        if img_urls is not None:
            company['img_urls'] = ','.join(img_urls)

        # info 最左边
        side_div = response.css('#side')
        user_info_div = side_div.xpath('div[@class="userinfo"]')
        company_name = get_first(user_info_div.xpath('h2/text()'))
        #logging.info(company_name)
        if company_name is not None:
            company_name = company_name.replace('\n','').replace('\t','').strip()
        company['name'] = company_name

        uinfolist = user_info_div.xpath('ul[@class="uinfolist"]')
        for li_tag in uinfolist.xpath('li'):
            i_name = get_first(li_tag.xpath('i/text()'))
            if i_name is not None:
                i_name = i_name.replace(u'\xa0','').replace(u' ','').replace(u'\u3000','').strip()
            if i_name == u'累计评价：':
                socre = get_first(li_tag.xpath('p/span/b/text()'))
                company['review_rating'] = socre
            if i_name == u'注册时间：':
                # 
                time = get_first(li_tag.xpath('p/text()'))
                if time is not None:
                    times = time.strip().split('.')
                    if len(times) == 3:
                        try:
                            d = datetime.date(year=int(times[0]),month=int(times[1]),day=int(times[2]))
                            company['user_join_date'] = d
                        except:
                            pass

            if i_name == u'地址：':  # 
                address = get_first(li_tag.xpath('p/text()'))
                company['address'] = address
            if i_name == u'信用档案：':
                # 此处爬取认证相关
                next_url = get_first(li_tag.xpath('p/a/@href'))

            if i_name == u'企业网站：':
                company['company_url'] = get_first(li_tag.xpath('div/a/@href'))
            if i_name == u'店铺：':
                company['user_url'] = get_first(li_tag.xpath('div/a/@href'))

            if i_name == u'用户名：':  # 
                user2_name = get_first(li_tag.xpath('p/text()'))
                if user2_name is not None:
                    user2_name = user2_name.strip()
                if 'user_name' not in company:
                    company['user_name'] = user2_name

        # qq
        qq_span = response.css('#qqWrapBox')
        if len(qq_span) == 1:
            qq_link = get_first(qq_span.xpath('a/@href'))
            company['qq_link'] = qq_link

        # 浏览次数
        count_str = get_first(response.css('#totalcount').xpath('text()'))
        try:
            company['views_count'] = int(count_str)
        except Exception:
            pass

        # 评价次数
        review_count_str = get_first(response.css('#pjxq').xpath('text()'))
        if review_count_str is not None:
            try:
                company['comments_count'] = int(review_count_str.replace('(', '').replace(')', ''))
            except Exception:
                pass



        #正则
        text = desc
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

                if len(rs)>=5:
                    qqs_list.append(rs)

            qqs = ",".join(set(qqs_list))

            tels_list = []
            for r in re.findall(re_tel,text):
                tels_list.append(str(r))
            for r in re.findall(re_mobi,text):
                tels_list.append(str(r))


            tels = ",".join(set(tels_list))

        company['additional_qqs'] = qqs
        company['mails'] = mails
        company['company_urls'] = company_urls
        company['additional_tels'] = tels

        if next_url is not None and next_url != '':
            yield scrapy.Request(next_url, meta={'company': company}, callback=self.parse_xinyong)
        else:
            yield company

    def parse_xinyong(self, response):
        #print 'get xinyong'
        company = copy.deepcopy(response.meta['company'])
        company['credit_url'] = response.url
        verify_div = response.xpath('//div[@class="verify"]')
        is_certified_weixin = False
        is_certified_company = False
        is_certified_person = False
        is_certified_email = False
        is_certified_tel = False

        for i_tag in verify_div.xpath('span/i'):
            i_tag_class = get_first(i_tag.xpath('@class'))
            if i_tag_class == 'weChat_yes':
                is_certified_weixin = True
            if i_tag_class == 'idCard_yes':
                # 原网页错误
                is_certified_company = True
            if i_tag_class == 'bussinesss_yes':
                is_certified_person = True
            if i_tag_class == 'mail_yes':
                is_certified_email = True
            if i_tag_class == 'tel_yes':
                is_certified_tel = True

        company['is_certified_tel'] = is_certified_tel
        company['is_certified_email'] = is_certified_email
        company['is_certified_person'] = is_certified_person
        company['is_certified_company'] = is_certified_company
        company['is_certified_weixin'] = is_certified_weixin

        yield company


    def noye_company_list(self, response):
        company = copy.deepcopy(response.meta['company'])
        table = response.css("#infolist").xpath('table')
        trs = table.xpath('tr')
        #logging.debug(table)
        #logging.debug(trs)
        logging.debug(len(trs))
        pattern2 = re.compile(r"\((\d{1,2})-(\d{1,2})\)")
        month = None
        day = None

        for tr in trs:
            temp_company = copy.deepcopy(company)
            div_t_tag = tr.xpath('td/div[@class="tdiv"]')
            if div_t_tag is None or len(div_t_tag) == 0:
                div_t_tag = tr.xpath('td')

            a_href = get_first(div_t_tag.xpath('a/@href'))
            next_url = a_href
            #next_url = urlparse.urljoin(response.url, a_href)
            is_best = get_first(div_t_tag.xpath('span[@class="jingpin"]'))
            is_top = get_first(div_t_tag.xpath('span[@class="ico ding"]'))

            if is_best is not None and is_best != '':
                #temp_company['is_best'] = True
                pass
                # todo
            if is_top is not None and is_top != '':
                temp_company['is_top'] = True

            tel = get_first(tr.xpath('td/b[@class="tele"]/text()'))
            if tel is not None:
                company['tel'] = tel.strip()

            # # 分页测试
            # div_text = ''.join(div_t_tag.xpath('text()').extract())
            # date_res = re.findall(pattern2,div_text)
            # if len(date_res) > 0:
            #     month = date_res[0][0]
            #     day = date_res[0][1]

            yield scrapy.Request(next_url, meta={'company': temp_company}, callback=self.noye_detail)

        next_a_tag = response.xpath('//div[@class="pager"]/a[@class="next"]')
        if len(next_a_tag) > 0:
            if right_date(month, day):
                next_page_href = get_first(next_a_tag.xpath('@href'))
                next_page_url = urlparse.urljoin(response.url, next_page_href)
                yield scrapy.Request(next_page_url, meta={'company': company}, callback=self.noye_company_list)



    def noye_detail(self, response):
        company = copy.deepcopy(response.meta['company'])
        company['ref_url'] = response.url
        title = get_first(response.xpath('//div[@class="w headline"]/h1/text()'))
        if title is not None:
            company['title'] = title.strip()

        guishu = get_first(response.xpath('//span[@class="belong"]/text()'))
        if guishu is not None:
            guishu = guishu.replace(u'（', '').replace(u'归属地：', '').replace(u'）', '').\
                    replace('\n','').replace('\t','').strip()
            company['mobile_addr'] = guishu

        info_ul = response.css('#info')
        for li_tag in info_ul.xpath('li'):
            i_name =  get_first(li_tag.xpath('i/nobr/text()'))
            aas =  li_tag.xpath('a')
            if i_name == u'详细地址：':
                if len(aas) > 0:
                    addr1 =get_first(aas[0].xpath('text()'))
                    company['addr1'] = addr1
                if len(aas) > 1:
                    addr2 =get_first(aas[1].xpath('text()'))
                    company['addr2'] = addr2
                if li_tag.xpath('text()').extract() is not None:
                    addr3 = li_tag.xpath('text()').extract()
                    #print 'addr3'
                    #print addr3
                    if addr3 is not None:
                        addr3 = ''.join(addr3).replace('-', '').replace('\n', '').replace('\t', '').strip()
                        company['addr3'] = addr3

            if i_name == u'类别：':
                thirdcategory = get_first(aas.xpath('text()'))
                if thirdcategory is not None:
                    company['third_category'] = thirdcategory

        desc1 = response.xpath('//div[@class="maincon"]//text()').extract()
        desc = None
        if desc1 is not None:
            desc = ''.join(desc1).replace('-', '').replace('\n', '').replace('\t', '').strip()
            company['desc'] = desc

        info_table = response.xpath('//table[@class="table"]')
        for tr_tag in info_table.xpath('tbody/tr'):
            th_name = get_first(tr_tag.xpath('th/text()'))

            if th_name is not None:
                th_name = th_name.strip()
            if th_name == u'公司名称：':
                name =  get_first(tr_tag.xpath('td/text()'))
                if name is not None:
                    company['name'] = name.strip()
            if th_name == u'公司网址：':
                co_url = get_first(tr_tag.xpath('td/a/@href'))
                company['company_url'] = co_url
            if th_name == u'联系地址：':
                address = get_first(tr_tag.xpath('td/text()'))
                company['address'] = address

            if th_name == u'商家认证：':
                span_class = tr_tag.xpath('td/span/@class').extract()
                if 'sfz' in span_class:
                    company['is_certified_person'] = True
                if 'yyzz' in span_class:
                    company['is_certified_company'] = True
                if 'sj' in span_class:
                    company['is_certified_tel'] = True
                if 'yx' in span_class:
                    company['is_certified_email'] = True

        img_pattern = re.compile(r'img_list\.push\("http://\w{3,5}\.58cdn\.com\.cn/[\w,/]{20,40}\.jpg')
        imgs = re.findall(img_pattern, response.body)
        imgs_url = [i.replace('img_list.push("', '') for i in imgs]
        if imgs_url is not None and len(imgs_url) >0:
            company['img_urls'] = ','.join(imgs_url)

        user_name_pattern = re.compile(r"linkman.*?,is_h")
        user_name = re.findall(user_name_pattern, response.body)
        if user_name is not None and len(user_name) > 0:
            company['user_name'] = user_name[0].replace("linkman:'",'').replace("'",'').replace(",is_h",'')

        # 浏览次数
        count_str = get_first(response.css('#totalcount').xpath('text()'))
        try:
            company['views_count'] = int(count_str)
        except Exception:
            pass




        #正则
        text = desc
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

                if len(rs)>=5:
                    qqs_list.append(rs)

            qqs = ",".join(set(qqs_list))

            tels_list = []
            for r in re.findall(re_tel,text):
                tels_list.append(str(r))
            for r in re.findall(re_mobi,text):
                tels_list.append(str(r))

            tels = ",".join(set(tels_list))

        company['additional_qqs'] = qqs
        company['mails'] = mails
        company['company_urls'] = company_urls
        company['additional_tels'] = tels

        yield company
