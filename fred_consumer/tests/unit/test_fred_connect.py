from django.test import TestCase
import urllib2
from fred_consumer.tests.unit.mock_urllib_response import MockUrlLibResponse
from fred_consumer.fred_connect import *
from fred_consumer.models import *
from fred_consumer.tests.unit.health_facility_id_map_factory import HealthFacilityIdMapFactory
import vcr, sys, os, fred_consumer
from healthmodels.models.HealthFacility import HealthFacilityBase

URLS = {
    'facility_base_url'  : FredConfig.get_fred_configs()['url'],
    'test_facility_url'  : FredConfig.get_fred_configs()['url'] + '/nBDPw7Qhd7r',
    'test_facility_url2' : FredConfig.get_fred_configs()['url'] +  '/pADPw7Qhd7r',
    'test_facility_id'   : 'nBDPw7Qhd7r',
    'test_facility_id2'  : 'pADPw7Qhd7r'
}

FRED_CONFIG = {"url": "http://dhis/api-fred/v1///", "username": "api", "password": "P@ssw0rd"}
FIXTURES = os.path.abspath(fred_consumer.__path__[0]) + "/tests/fixtures/cassettes/"

class TestFredFacilitiesFetcher(TestCase):

    def setUp(self):
        FredConfig.store_fred_configs(FRED_CONFIG)
        self.fetcher = FredFacilitiesFetcher(FredConfig.get_fred_configs())


    def test_get_all_facilities(self):
      with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
        obj = self.fetcher.get_all_facilities()
        self.assertIsNotNone(obj)

    def test_get_facility(self):
      with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
        obj = self.fetcher.get_facility(URLS['test_facility_id'])
        self.assertIsNotNone(obj)

    def test_get_filtered_facilities(self):
      with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
        obj = self.fetcher.get_filtered_facilities({'updatedSince': '2013-01-16T00:00:00Z'});
        self.assertIsNotNone(obj)

    def test_process_facility(self):
      with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/test_get_all_facilities.yaml"):
        obj = self.fetcher.get_all_facilities()
        facility = obj['facilities'][0]
        uuid = '6VeE8JrylXn'
        assert len(HealthFacilityIdMap.objects.filter(uuid=uuid)) == 0
        assert len(HealthFacilityBase.objects.filter(uuid=uuid)) == 0
        self.fetcher.process_facility(facility)
        self.failUnless(HealthFacilityBase.objects.filter(uuid=uuid)[0])
        self.failUnless(HealthFacilityIdMap.objects.filter(uuid=uuid)[0])