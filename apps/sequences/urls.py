from django.conf.urls import patterns, url
# from django.conf import settings
# from django.views.decorators.cache import cache_page

from apps.sequences.views import create_sequence, sequence_list

urlpatterns = patterns('',
        # url(r'^select/sequences/$', get_objects, name='select_sequences'),
        url(r'^create/sequence/$', create_sequence, name='create_sequence'),
        url(r'^select/sequence/$', sequence_list, name='sequence_list'),
        url(r'^sequence/(?P<sequence_id>\d+)/$', create_sequence, name='sequence_edit'),
        # url(r'^object/(?P<object_id>\d+)/$', update_object, name='update_object'),
    )