from django.test import TestCase
from django.core import management
from fred_consumer.models import *
from django.db import IntegrityError

class TestFredConfig(TestCase):

  def test_uniqueness_on_key(self):
    config = FredConfig.objects.create(key="KEY", value="VALUE")
    self.failUnless(config.id)

    new_config = FredConfig()
    new_config.key = "KEY"
    new_config.value = "VALUE"
    self.failUnlessRaises(IntegrityError, new_config.save)

  def test_get_fred_configs(self):
    url = "http://fred-provider.com/api/v1/"
    username = "django"
    password = "django"
    assert FredConfig.get_fred_configs() == {"url": "", "username": "", "password": ""}
    FredConfig.objects.create(key=FredConfig.URL_KEY      , value=url)
    FredConfig.objects.create(key=FredConfig.USERNAME_KEY , value=username)
    FredConfig.objects.create(key=FredConfig.PASSWORD_KEY , value=password)
    assert FredConfig.get_fred_configs() == {"url": url, "username": username, "password": password}

  def test_store_fred_configs(self):
    url = "http://fred-provider.com/api/v1/"
    username = "django"
    password = "django"
    params = {"url": url, "username": username, "password": password}
    FredConfig.store_fred_configs(params)
    assert FredConfig.get_fred_configs() == params