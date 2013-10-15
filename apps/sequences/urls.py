from django.conf.urls import patterns, url

from apps.sequences.views import create_sequence, sequence_list

urlpatterns = patterns('',
        url(r'^create/sequence/$', create_sequence, name='create_sequence'),
        url(r'^select/sequence/$', sequence_list, name='sequence_list'),
        url(r'^sequence/(?P<sequence_id>\d+)/$', create_sequence, name='sequence_edit'),
    )