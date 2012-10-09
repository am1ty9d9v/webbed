#/*********************************************************************************************

#Project : A web crawler cum search engine
#URI: http://www.webbed.co.cc/
#Version: 1.0
#Author: Amit Yadav
#Author URI: http://www.amityadav.in
#Github URI: https://github.com/am1ty9d9v/webbed

#**********************************************************************************************


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
