from django.contrib.auth.decorators import login_required
from django.conf.urls.defaults import patterns, url
from fred_consumer.views import *

urlpatterns = patterns('',
                      url(r'^$', login_required(fred_config_page), name="fred_config_page"),
                      url(r'^sync_now/$', login_required(sync_now), name="sync_now"),
                      url(r'^terminate_job/$', login_required(terminate_job), name="terminate_job"),
                      url(r'^failures/$', login_required(failures), name="failures"),
                      )