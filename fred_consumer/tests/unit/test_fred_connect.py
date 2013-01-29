from django.test import TestCase
import urllib2
from fred_consumer.tests.unit.mock_urllib_response import MockUrlLibResponse
from fred_consumer.fred_connect import *
from fred_consumer.models import *
from fred_consumer.tests.unit.health_facility_id_map_factory import HealthFacilityIdMapFactory
import vcr, sys, os, fred_consumer
from healthmodels.models.HealthFacility import HealthFacilityBase, HealthFacilityType
from mock import *
from fred_consumer.tasks import *
import json

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

    @patch('fred_consumer.tasks.process_facility.delay')
    def test_sync(self, mock_process_facility):
      with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/test_get_all_facilities.yaml"):
        self.fetcher.sync()
      assert mock_process_facility.called

    def test_process_facility(self):
      facility_json = json.loads('{"facilities":[{"id":"6VeE8JrylXn","name":" BATMAN HC II","active":true,"url":"http://dhis/api-fred/v1/facilities/6VeE8JrylXn","createdAt":"2012-08-14T10:00:07.701+0000","updatedAt":"2013-01-22T15:09:55.543+0000","coordinates":[2.2222,0.1111],"properties":{"level":1,"hierarchy":[{"id":"OwhPJYQ9gqM","level":1,"name":"MOH-Uganda","url":"http://dhis/api/organisationUnitLevels/OwhPJYQ9gqM"},{"id":"V9O2FgyImDt","level":2,"name":"Region","url":"http://dhis/api/organisationUnitLevels/V9O2FgyImDt"},{"id":"a1XiGwfbe81","level":3,"name":"District","url":"http://dhis/api/organisationUnitLevels/a1XiGwfbe81"},{"id":"fgJNYG1Ps13","level":4,"name":"Sub-County","url":"http://dhis/api/organisationUnitLevels/fgJNYG1Ps13"},{"id":"G5kUCanhxGU","level":5,"name":"Health Unit","url":"http://dhis/api/organisationUnitLevels/G5kUCanhxGU"}]}}]}')['facilities'][0]

      uuid = facility_json['id']
      HealthFacilityType.objects.filter(name="hcii").delete()
      HealthFacilityBase.objects.filter(uuid=uuid).delete()

      HealthFacilityType.objects.create(name="hcii")

      facility = HealthFacilityBase.objects.create(uuid=uuid, name="BATMAN")
      self.failUnless(facility.id)

      assert len(HealthFacilityIdMap.objects.filter(uuid=uuid)) == 0
      assert len(HealthFacilityBase.objects.filter(uuid=uuid)) == 1

      fred_consumer.tasks.process_facility(facility_json)

      facility = HealthFacilityBase.objects.filter(uuid=uuid)[0]
      self.failUnless(facility)
      self.failUnless(HealthFacilityIdMap.objects.filter(uuid=uuid)[0])
      assert facility.name == "BATMAN HC II"
