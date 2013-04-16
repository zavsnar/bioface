from django.conf.urls import patterns, url

from apps.attributes.views import attribute_list, create_attribute, edit_attribute
from apps.attributes.ajax import ajax_change_attribute

urlpatterns = patterns('',
        url(r'^attributes/$', attribute_list, name='attributes'),
        url(r'^create/attribute/$', create_attribute, name='create_attribute'),
        url(r'^attribute/(?P<attr_id>.*)/$', edit_attribute, name='edit_attribute'),
        # url(r'^delete/attribute/$', delete_attribute, name='delete_attribute'),
        url(r'^ajax/change-attribute/$', ajax_change_attribute, name='ajax_change_attribute'),
        # url(r'^ajax/change-attribute-default/$', ajax_change_attribute_default, 
        #     name='ajax_change_attribute_default'),
    )