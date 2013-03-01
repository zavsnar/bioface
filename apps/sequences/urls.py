from django.conf.urls import patterns, url, include
from django.conf import settings
# from django.views.decorators.cache import cache_page

from apps.sequences.views import create_sequence

urlpatterns = patterns('',
        # url(r'^select/sequences/$', get_objects, name='select_sequences'),
        url(r'^create/sequence/$', create_sequence, name='create_sequence'),
        # url(r'^object/(?P<object_id>\d+)/$', update_object, name='update_object'),
    )