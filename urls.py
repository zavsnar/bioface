from django.conf.urls import patterns, url, include
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.views import login
# from django.views.decorators.cache import cache_page

# from django.contrib.sitemaps import views as sitemaps_views
from django.contrib import admin

# from sitemaps import scheme as sitemaps
from apps.bioface.views import signin, registration, logout, request_api_page, alter_index, create_update_item

admin.autodiscover()

from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()

# robots_txt view
# robots_txt = "User-agent: *\nDisallow: /" if settings.DISALLOW_SEARCH_ROBOTS else ''
# get_robots_txt = lambda r: HttpResponse(robots_txt, mimetype="text/plain")

urlpatterns = patterns('',
        url(r'^$', request_api_page, name='index'),
        url(r'^alter-index/$', alter_index, name='alter_index'),
        url(r'^login/$', signin, name='signin'),
        url(r'^logout/$', logout, name='logout'),
        url(r'^registration/$', registration, name='registration'),

        url(r'^create/$', create_update_item, name='create_update_item'),
#         url(r'^terms/$', render, kwargs={'template_name': 'terms.html'}, name='terms'),
#         url(r'^support/$', render, kwargs={'template_name': 'support.html'}, name='support'),

#         url(r'^', include('apps.tasks.urls')),
#         url(r'^', include('apps.accounts.urls')),
#         url(r'^', include('apps.eway_au.urls')),

#         url(r'^' + settings.ADMIN_SITE_PREFIX[1:], include(admin.site.urls)),
#         url(r'^robots\.txt$', get_robots_txt),
#         url(r'^sitemap\.xml$', cache_page(5*60)(sitemaps_views.sitemap), kwargs={'sitemaps': sitemaps})
    )

if settings.DEBUG:
    urlpatterns += patterns('',
            # url(r'^404/$', render, kwargs={'template_name': '404.html'}, name='404'),
            # url(r'^500/$', render, kwargs={'template_name': '500.html'}, name='500'),
            (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
            (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
            url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
        )



from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()