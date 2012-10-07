from django.conf.urls import patterns, include, url
from webbed.views import search, search_results, crawl_now, feedback
from django.contrib import admin
from django.views.generic.simple import direct_to_template

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', search),
    (r'^feedback/$', feedback),
    (r'^search/', search_results),
    (r'^update_index/', crawl_now),
    (r'^admin/', include(admin.site.urls)),
)
