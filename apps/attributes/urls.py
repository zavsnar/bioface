from django.conf.urls import patterns, url
# from django.conf import settings
# from django.views.decorators.cache import cache_page

from apps.attributes.views import attribute_list, create_attribute, edit_attribute

urlpatterns = patterns('',
        url(r'^attributes/$', attribute_list, name='attributes'),
        url(r'^create/attribute/$', create_attribute, name='create_attribute'),
        url(r'^attribute/(?P<attr_id>.*)$', edit_attribute, name='edit_attribute'),
    )