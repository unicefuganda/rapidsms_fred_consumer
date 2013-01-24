from django.contrib.auth.decorators import login_required
from django.conf.urls.defaults import patterns, url
from fred_consumer.views import *

urlpatterns = patterns('',
                      url(r'^$', login_required(fred_config_page), name="fred_config_page"),
                      url(r'^update_config/$', login_required(fred_update_config), name="fred_update_config"),
                      )