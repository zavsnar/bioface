from django.conf.urls import patterns, url, include
from django.conf import settings
# from django.views.decorators.cache import cache_page

from apps.attributes.views import attribute_list

urlpatterns = patterns('',
        url(r'^attributes/$', attribute_list, name='attributes'),
    )