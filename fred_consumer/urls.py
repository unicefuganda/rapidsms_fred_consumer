from django.conf.urls.defaults import patterns, url
from fred_consumer.views import *

urlpatterns = patterns('',
                      url(r'^$', fred_config_page, name="fred_config_page"),
                      url(r'^update_config/$', fred_update_config, name="fred_update_config"),
                      )