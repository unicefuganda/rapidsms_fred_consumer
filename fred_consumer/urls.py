from django.conf.urls.defaults import patterns, url
from fred_consumer.views import fred_config_page

urlpatterns = patterns('',
                      url(r'^$', fred_config_page, name="fred_config_page"),
                      )