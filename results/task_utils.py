#Stage 2 Update (Python 3)
from future import standard_library
standard_library.install_aliases()
from builtins import object
import datetime, json
import urllib.request, urllib.parse, http.client
from scrapy.utils.project import get_project_settings
settings = get_project_settings()
from dynamic_scraper.models import Scraper

# 此文件是对 原 dds 框架bug的修复版


class TaskUtils(object):
    
    conf = {
        "MAX_SPIDER_RUNS_PER_TASK": 10,
        "MAX_CHECKER_RUNS_PER_TASK": 25,
    }
    
    def _run_spider(self, **kwargs):
        param_dict = {
            'project': 'default',
            'spider': kwargs['spider'],
            'id': kwargs['id'],
            'run_type': kwargs['run_type'],
            'do_action': kwargs['do_action']
        }
        params = urllib.parse.urlencode(param_dict)
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        conn = http.client.HTTPConnection("localhost:6800")
        conn.request("POST", "/schedule.json", params, headers)
        conn.getresponse()
    
    
    def _pending_jobs(self, spider):
        # Ommit scheduling new jobs if there are still pending jobs for same spider
        resp = urllib.request.urlopen('http://localhost:6800/listjobs.json?project=default')
        data = json.load(resp)
        if 'pending' in data:
            for item in data['pending']:
                if item['spider'] == spider:
                    return True
        return False
    
    
    def run_spiders(self, ref_obj_class, ref_obj_id, scraper_field_name, runtime_field_name, spider_name, *args, **kwargs):
        filter_kwargs = {
            '%s__status' % scraper_field_name: 'A',
            '%s__next_action_time__lt' % runtime_field_name: datetime.datetime.now(),
        }
        for key in kwargs:
            filter_kwargs[key] = kwargs[key]
        
        max = settings.get('DSCRAPER_MAX_SPIDER_RUNS_PER_TASK', self.conf['MAX_SPIDER_RUNS_PER_TASK'])
        ref_obj_list = ref_obj_class.objects.filter(id=ref_obj_id).filter(*args, **filter_kwargs).order_by('%s__next_action_time' % runtime_field_name)[:max]
        if not self._pending_jobs(spider_name):
            for ref_object in ref_obj_list:
                self._run_spider(id=ref_object.pk, spider=spider_name, run_type='TASK', do_action='yes')
        

    def run_checkers(self, ref_obj_class, scraper_field_path, runtime_field_name, checker_name, *args, **kwargs):
        filter_kwargs = {
            '%s__status' % scraper_field_path: 'A',
            '%s__next_action_time__lt' % runtime_field_name: datetime.datetime.now(),
        }
        for key in kwargs:
            filter_kwargs[key] = kwargs[key]
        
        max = settings.get('DSCRAPER_MAX_CHECKER_RUNS_PER_TASK', self.conf['MAX_CHECKER_RUNS_PER_TASK'])
        ref_obj_list = ref_obj_class.objects.filter(*args, **filter_kwargs).order_by('%s__next_action_time' % runtime_field_name)[:max]
        if not self._pending_jobs(checker_name):
            for ref_object in ref_obj_list:
                self._run_spider(id=ref_object.pk, spider=checker_name, run_type='TASK', do_action='yes')

