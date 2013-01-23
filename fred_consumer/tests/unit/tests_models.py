from django.test import TestCase
from django.core import management
from mtrack_project.rapidsms_fred_consumer.fred_consumer.models import *
from django.db import IntegrityError

class TestFredConfig(TestCase):

  def test_store_config(self):
    config = FredConfig.objects.create(key="URL", value="http://fred-provider.com/api/v1/")
    self.failUnless(config.id)

  def test_uniqueness_on_key(self):
    config = FredConfig.objects.create(key="KEY", value="VALUE")
    self.failUnless(config.id)

    new_config = FredConfig()
    new_config.key = "KEY"
    new_config.value = "VALUE"
    self.failUnlessRaises(IntegrityError, new_config.save)