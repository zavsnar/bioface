from django.conf.urls import patterns, url, include
from django.conf import settings
from django.contrib import admin

from apps.common.views import index, signin, registration, logout, create_organism
from apps.persons.views import downloads_list

admin.autodiscover()

from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()

urlpatterns = patterns('',
        url(r'^$', index, name='index'),

        url(r'^login/$', signin, name='signin'),
        url(r'^logout/$', logout, name='logout'),
        url(r'^registration/$', registration, name='registration'),

        url(r'^my-downloads/$', downloads_list, name='downloads_list'),

        url(r'^', include('apps.objects.urls')),
        url(r'^', include('apps.attributes.urls')),
        url(r'^', include('apps.sequences.urls')),

        url(r'^create/organism/$', create_organism, name='create_organism'),

        # include dajax urls
        url(dajaxice_config.dajaxice_url, include('dajaxice.urls'))
    )

if settings.DEBUG:
    # media and static in DEBUG state
    urlpatterns += patterns('',
            (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
            (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
        )

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()