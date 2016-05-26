# 不同的执行方式

## 命令行执行
- 在运行前 ps -ef | grep scrapy 检查是否有之前的爬虫运行

nohup ./server.sh &
nohup scrapy crawl dianping_general_spider -a id=3 -a do_action=yes&
nohup scrapy crawl wuba_general_spider_20160126 -a id=4 -a do_action=yes&
nohup scrapy crawl baixing_general_spider -a id=2 -a do_action=yes &

- 以上命令中id 指的是对应的 yt_website 的 id
- wuba_general_spider_20160126 是新版本58 sh.58.com/huangye 的爬虫name 
	此处name 不是文件名而是 class spider 的 name 属性


## scraypd 部署执行

1 部署 若无修改仅需部署一次

在 项目文件夹下 scrapyd-deploy default -p source 
default 指项目名 为 default

- 运行后有结果提示 status ok 正常。 例如
- {"status": "ok", "project": "source", "version": "1454052895", "spiders": 8, "node_name": "yzyubuntu"}



2 django 和 celery

nohup ./server.sh &
nohup python manage.py celeryd -l info -B --settings=aragog.settings &

- 注意 locations view.py 中对city 的选取 为所有 level =2 的aa

3. admin

在admin 中 djcelery Periodic tasks中添加定时任务
