from django.test import TestCase
import urllib2
from fred_consumer.tests.unit.mock_urllib_response import MockUrlLibResponse
from fred_consumer.fred_connect import *
from fred_consumer.models import *
from fred_consumer.tests.unit.health_facility_id_map_factory import HealthFacilityIdMapFactory

URLS = {
    'facility_base_url'  : FredConfig.get_fred_configs()['url'],
    'test_facility_url'  : FredConfig.get_fred_configs()['url'] + '/nBDPw7Qhd7r',
    'test_facility_url2' : FredConfig.get_fred_configs()['url'] +  '/pADPw7Qhd7r',
    'test_facility_id'   : 'nBDPw7Qhd7r',
    'test_facility_id2'  : 'pADPw7Qhd7r'
}

FRED_CONFIG = {"url": "http://fred-provider.com/api/v1/facilities///", "username": "django", "password": "django"}

class TestFacilityMatcher(TestCase):

    def setUp(self):
        FredConfig.store_fred_configs(FRED_CONFIG)
        self.fetcher = FredFacilitiesFetcher(FredConfig.get_fred_configs())
        urllib2.urlopen = mock_urlopen


    def test_get(self):
        obj = self.fetcher.get()
        self.assertIsNotNone(obj)

    def test_get_facility(self):
        obj = self.fetcher.get_facility(URLS['test_facility_id'])
        self.assertIsNotNone(obj)

    def test_get_filtered_facilities(self):
        obj = self.fetcher.get_filtered_facilities({'updatedSince': '2012-11-16T00:00:00Z'});
        self.assertIsNotNone(obj)


def mock_urlopen(request):
    import os
    filedir = os.path.dirname(__file__)
    json_filename = request.get_full_url().rsplit('/',1)[-1].rsplit('?',1)[0]
    path = os.path.join(filedir,'../fixtures/%s' % json_filename)
    jason = open(path).read()
    return MockUrlLibResponse(jason)
