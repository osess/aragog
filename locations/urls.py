#coding:utf-8
from django.conf.urls import url

from . import views

# urlpatterns = patterns('locations.views',
#     url(r'^china_cities/$', get_china_cities, name='china_cities'),
# )
urlpatterns = [
    url(r'^china_cities/$', views.get_china_cities, name='china_cities'),
]
