# coding:utf-8
# Scrapy settings for open_news project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

import os, sys

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aragog.settings")
sys.path.insert(0, os.path.join(PROJECT_ROOT, "../../..")) #only for aragog


BOT_NAME = 'sources'

SPIDER_MODULES = [
    'dynamic_scraper.spiders',
    'sources.scraper',
    'results.scraper'
    ]

#USER_AGENT = '%s/%s' % (BOT_NAME, '1.0')

ITEM_PIPELINES = {
    #'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,  # 禁止原ua
    #'sources.scraper.middle.RotateUserAgentMiddleware': 100,

    'dynamic_scraper.pipelines.DjangoImagesPipeline': 200,
    'dynamic_scraper.pipelines.ValidationPipeline': 400,
    'sources.scraper.pipelines.CategoryValitionPipeline': 800,  # 分类匹配
    'sources.scraper.pipelines.CityPipeline': 810,  # yt_city 字段处理
    'results.scraper.pipelines.DataCleanPipeline': 820,  # 脏数据清理

    # 一般的pipeline 放在MatchPipeline以上
    'results.scraper.pipelines.MatchPipeline': 900,  # 匹配后处理 将不匹配的改为 另一个item
    # 以下为保存 处理重复 有匹配/不匹配两种情况
    'results.scraper.pipelines.WubaItemPipeline': 910,
    'results.scraper.pipelines.DianpingItemPipeline': 920,
    'results.scraper.pipelines.BaixingItemPipeline': 930,
}

IMAGES_STORE = os.path.join(PROJECT_ROOT, '../thumbnails')

IMAGES_THUMBS = {
    'medium': (50, 50),
    'small': (25, 25),
}

DSCRAPER_IMAGES_STORE_FORMAT = 'ALL'

DSCRAPER_LOG_ENABLED = True
#DSCRAPER_LOG_LEVEL = 'DEBUG'
DSCRAPER_LOG_LEVEL = 'INFO'
DSCRAPER_LOG_LIMIT = 5


RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_DELAY=1

#LOG_LEVEL = 'DEBUG'
LOG_LEVEL = 'INFO'
LOG_FILE = 'yt_spider_dp.log'


USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'