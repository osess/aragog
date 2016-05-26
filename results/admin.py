from django.contrib import admin
# from open_news.models import NewsWebsite, Article
from results.models import Wuba, Dianping, Baixing
from results.models import DianpingNotmatch, BaixingNotmatch, WubaNotmatch

admin.site.register(Wuba)
admin.site.register(Dianping)
admin.site.register(Baixing)
admin.site.register(WubaNotmatch)
admin.site.register(DianpingNotmatch)
admin.site.register(BaixingNotmatch)

