import unittest
from mtrack_project.rapidsms_fred_consumer.fred_consumer.models import *

class TestFredConfig(unittest.TestCase):
  def test_store_config(self):
    config = FredConfig.objects.create(url="http://fred-provider.com/api/v1/", username="django", password="django")
    self.failUnless(config.id)
