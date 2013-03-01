from django.conf.urls import patterns, url, include
from django.conf import settings
# from django.views.decorators.cache import cache_page

from apps.objects.views import create_object, update_object, get_objects, import_uploader

urlpatterns = patterns('',
        url(r'^select/objects/$', get_objects, name='select_objects'),
        url(r'^create/object/$', create_object, name='create_object'),
        url(r'^object/(?P<object_id>\d+)/$', update_object, name='update_object'),

        url(r'^ajax-upload/$', import_uploader, name="my_ajax_upload"),
    )