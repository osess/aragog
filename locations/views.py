#coding:utf-8

# sys
import datetime
from urllib2 import HTTPError

# django
from django.utils.translation           import ugettext
from django.contrib.auth.models         import User
from django.shortcuts                   import render
from django.shortcuts                   import get_object_or_404
from django.shortcuts                   import render_to_response
from django.db.models                   import Q
from django.template                    import RequestContext
from django.http                        import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators     import login_required
from django.core.urlresolvers           import reverse
from django.utils.translation           import ugettext as _

from locations.models                   import AdministrativeArea


def get_china_cities(request):
    # todo
    cities = AdministrativeArea.objects.filter(level=2)
    #cities = cities.filter(factor__lte=4)[0:1]
    cities = cities.filter(slug='shanghai,shanghai')

    return render(request, 'locations/china_cities.html', {'cities': cities})
