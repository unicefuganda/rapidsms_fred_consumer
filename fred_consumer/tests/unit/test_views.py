from django.test import TestCase
from django.test.client import Client

class TestViews(TestCase):

  def test_fred_config_page(self):
    client = Client()
    response = client.get('/fredconsumer/')
    self.assertEqual(response.status_code, 200)