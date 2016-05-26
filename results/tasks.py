# coding:utf-8
from celery.task import task

#from dynamic_scraper.utils.task_utils import TaskUtils
from .task_utils import TaskUtils

from sources.models import Website
from .models import Wuba


@task()
def run_spider(website_id, spider_name):
    t = TaskUtils()
    t.run_spiders(Website, website_id, 'scraper', 'scraper_runtime', spider_name)


# @task()
# def run_spider(website_id, spider_name):
#     t = TaskUtils()
#     t.run_spiders(Website, website_id, 'scraper', 'scraper_runtime', spider_name)


# @task()
# def check_spider_status():
#     # 检测爬虫的状态
#     url = 'http://localhost:6800'
#     project_name = 'default'

#     def set_or_update(project_name, status, data):
#         from sources.models import SpiderStatus
#         for d in data:
#             ss = SpiderStatus.objects.filter()

#     from scrapyd_api import ScrapydAPI
#     scrapyd = ScrapydAPI(url)
#     result_dict = scrapyd.list_jobs(project_name)

#     if result_dict['status'] != 'ok':
#         pass
#         # log

#     else:
#         pendings = result_dict['pending']
#         runnings = result_dict['running']
#         finisheds = result_dict['finished']
        

# @task()
# def test(arg1, arg2):
#     print arg1
#     print arg2

