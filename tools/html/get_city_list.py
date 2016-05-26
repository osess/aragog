#coding:utf-8

import sys
import os

# Setup environ
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../..'))

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aragog.settings")
django.setup()

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# ----------------------------------------------------------------------------
import requests
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq

from locations.models import AdministrativeArea
from django.db.models import Q


wuba_url = "http://www.58.com/changecity.aspx?PGTID=0d100000-0000-29a1-1eec-3adf4b8ca78f&ClickID=1"
wuba_file = "wuba.html"

baixing_url = "http://www.baixing.com/?changeLocation=yes"
baixing_file = "baixing.html"

dianping_url = "http://www.dianping.com/citylist/citylist?citypage=1"
diangping_file = "dianping.html"

province_center = []


# -----------------------------------
# 58 未处理
"""
顺德
明港
神农架
海拉尔
巴音郭楞
博尔塔拉
克孜勒苏
香港
澳门
台湾
钓鱼岛
其他
洛杉矶
旧金山
纽约
多伦多
温哥华
蒙特利尔
伦敦
首尔
东京
新加坡
吉隆坡
曼谷
悉尼
墨尔本
其他海外城市
"""

# 百姓
"""
神农架
澄迈
定安
临高
屯昌
博尔塔拉
巴音郭楞
克孜勒苏
"""
# 点评

"""

石柱土家族自治县
台湾
香港
澳门
花莲
高雄
台南
桃园
新北
台中
垦丁
阿里山
南投
基隆
台东
嘉义
宜兰
新竹
彰化
苗栗
南戴河
任丘市
内丘县
更多
土默特左旗
达尔罕茂明安联合旗
科尔沁左翼后旗
陈巴尔虎旗
察哈尔右翼中旗
科尔沁右翼前旗
科尔沁右翼中旗
亚布力
杜尔伯特蒙古族自治县
更多
长白山
更多
岫岩满族自治县
北宁市
更多
周庄
天目湖
甪直
同里
更多
西塘
乌镇
富春江
千岛湖
天目山
雁荡山
莫干山
横店
朱家尖
普陀山
仙都
上虞区
柯桥区
更多
天柱山
宏村
西递
九华山
鼓浪屿
更多
临颍县
武当山
三峡
随县
汨罗市
江华瑶族自治县
靖州苗族侗族自治县
更多
三清山
龙虎山
明月山
共青城市
更多
花水湾
西岭雪山
青城山
天台山
泸沽湖
德昌县
更多
喜洲
双廊
石林彝族自治县
禄劝彝族苗族自治县
寻甸回族彝族自治县
峨山彝族自治县
新平彝族傣族自治县
元江哈尼族彝族傣族自治县
玉龙纳西族自治县
宁蒗彝族自治县
普洱哈尼族彝族自治县
墨江哈尼族自治县
景东彝族自治县
景谷傣族彝族自治县
镇沅彝族哈尼族拉祜族自治县
江城哈尼族彝族自治县
孟连傣族拉祜族佤族自治县
澜沧拉祜族自治县
西盟佤族自治县
双江拉祜族佤族布朗族傣族自治县
耿马傣族佤族自治县
沧源佤族自治县
贡山独龙族怒族自治县
兰坪白族普米族自治县
维西傈僳族自治县
漾濞彝族自治县
南涧彝族自治县
巍山彝族回族自治县
金平苗族瑶族傣族自治县
河口瑶族自治县
屏边苗族自治县
更多
黄果树
西江千户苗寨
白云山
关岭布依族苗族自治县
更多
堆龙德庆县
察雅县
双湖县
巴音郭楞
博尔塔拉
克孜勒苏
北屯
塔什库尔干塔吉克自治县
巴里坤哈萨克自治县
玛纳斯县
木垒哈萨克自治县
焉耆回族自治县
察布查尔锡伯自治县
阿拉山口市
青海湖
民和回族土族自治县
互助土族自治县
循化撒拉族自治县
门源回族自治县
河南蒙古族自治县
更多
华山
张家川回族自治县
天祝藏族自治县
安西县
阿克塞哈萨克族自治县
积石山保安族东乡族撒拉族自治县
连山壮族瑶族自治县
更多
涠洲岛
恭城瑶族自治县
更多
博鳌
更多

"""




def get_city(city_name):
    try:
        cities = AdministrativeArea.objects.filter(Q(short_name=city_name, level__in=[2,3])|Q(name=city_name, level__in=[2,3]))
    except Exception:
        return None

    if cities.count() == 0:
        return None

    if cities.count() > 1:
        if cities.filter(level=2).count() ==1:
            return cities.filter(level=2)[0]
        else:
            return None

    return cities[0]


def get_text(url):
    cookies = dict(rfb='1',__city='shanghai')
    r = requests.get(url)
    return r.content


def parse_wuba_text(text):
    soup = BeautifulSoup(text)
    clist = soup.find(id='clist')
    alist = clist.find_all('a')
    res = []
    for a in alist:
        temp = list()
        temp.append(a.string)
        temp.append(a['href'])
        res.append(temp)

    return res

def write_to_file(res,file_name):
    f = open(file_name,'w')
    slist = []
    for r in res:
        s = "<li><a href='%s'>%s</a</li>\n" % (r[1], r[0])
        if r[0] in province_center:
            s = "<li class='province_center' ><a href='%s'>%s</a</li>\n" % (r[1], r[0]) 
    #   print s
    #   print type(s)
        slist.append(str(s))
    f.writelines(slist)
    f.close()

#print 'done'

def parse_baixing_text(text):
    soup = BeautifulSoup(text)
    div = soup.find_all('ul', class_='wrapper')[0]
    alist = div.find_all('a')
    res = []
    for a in alist:
        temp = []
        temp.append(a.string)
        temp.append(str(a['href']))
        res.append(temp)
    return res


def parse_dianping_text(text):
    soup = BeautifulSoup(text)
    div = soup.find_all('div', class_="city-list J-city-list Hide")[0]
    alist = div.find_all('a')
    res = []
    for a in alist:
        temp = []

        temp.append(a.string)
        temp.append(str(a['href']))
        res.append(temp)
    return res


def parse_dianping_text2(text):
    soup = BeautifulSoup(text)
    ul = soup.find('ul', id='divArea')
    res = []
    for li in ul.find_all('li'):
        for dl in li.find_all('dl'):
            for dd in dl.find_all('dd'):
                for a in dd.find_all('a'):
                    temp = []
                    name = a.string
                    href = str(a['href'])
                    temp.append(name)
                    tem.append(href)
    return res

def parse_dianping_text3(text):
    soup = BeautifulSoup(text)
    ul = soup.find_all('ul', id='divArea')[0]
    alist = ul.find_all('a')
    res = []
    for a in alist:
        temp = []

        temp.append(a.string)
        temp.append(str(a['href']))
        res.append(temp)
    return res


def insert_into_db(city, url, field_name):
    if city is None or field_name is None:
        # log
        return

    if field_name == 'wuba_url':
        city.wuba_url = url
    if field_name == 'baixing_url':
        city.baixing_url = url
    if field_name == 'dianping_url':
        city.dianping_url = url
    city.save()



def wuba():
    print 'wuba start'
    text = get_text(wuba_url)
    res = parse_wuba_text(text)

    for r in res:
        city = get_city(r[0])
        url = r[1]
        if city is None:
            # log
            print r[0]
        else:
            insert_into_db(city, url, 'wuba_url')
            pass

def baixing():
    print 'baixing start'
    text = get_text(baixing_url)
    res = parse_baixing_text(text)

    for r in res:
        city = get_city(r[0])
        url = r[1]
        if city is None:
            # log
            print r[0]
        else:
            insert_into_db(city, url, 'baixing_url')
            pass


def dianping():
    print 'diangping start'
    text = get_text(dianping_url)
    res = parse_dianping_text3(text)

    for r in res:
        if r[0] != u'更多':
            city = get_city(r[0])
            url = "http://www.dianping.com" + r[1]
            if city is None:
                # log
                print r[0]
            else:
                insert_into_db(city, url, 'dianping_url')
                pass



def main():
    # text = get_text(wuba_url)
    # res = parse_wuba_text(text)
    # write_to_file(res, wuba_file)
    # # --------------------------
    # text = get_text(dianping_url)
    # res = parse_dianping_text(text)
    # write_to_file(res, dianping_file)
    print 'main start...'
    #wuba()
    #baixing()
    dianping()




if __name__ == "__main__":
    main()
