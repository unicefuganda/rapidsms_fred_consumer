import unittest
import urllib2
from fred_consumer.tests.unit.mock_urllib_response import MockUrlLibResponse
from fred_consumer.fred_connect import *
from fred_consumer.models import HealthFacilityIdMap
from fred_consumer.tests.unit.health_facility_id_map_factory import HealthFacilityIdMapFactory

CONNECTION_SETTING = {
  'user': 'sekiskylink',
  'password': '123Congse'
}

URLS = {
  'facility_base_url': 'http://ec2-54-242-108-118.compute-1.amazonaws.com/api-fred/v1/facilities',
  'test_facility_url' :'http://ec2-54-242-108-118.compute-1.amazonaws.com/api-fred/v1/facilities/nBDPw7Qhd7r',
  'test_facility_url2' :'http://ec2-54-242-108-118.compute-1.amazonaws.com/api-fred/v1/facilities/pADPw7Qhd7r',
  'test_facility_id' : 'nBDPw7Qhd7r',
  'test_facility_id2' : 'pADPw7Qhd7r'
}

class TestFacilityMatcher(unittest.TestCase):

    def setUp(self):
        self.fetcher = FredFacilitiesFetcher(CONNECTION_SETTING)


    def test_get(self):
        urllib2.urlopen = mock_urlopen

        obj = self.fetcher.get(URLS['facility_base_url']);
        self.assertIsNotNone(obj)

        obj = self.fetcher.get(URLS['test_facility_url'])
        self.assertIsNotNone(obj)

        obj = self.fetcher.get(URLS['test_facility_url'],paging=False);
        self.assertIsNotNone(obj)


    def test_get_facility(self):
        urllib2.urlopen = mock_urlopen
        obj = self.fetcher.get_facility(URLS['facility_base_url'],URLS['test_facility_id']);
        self.assertIsNotNone(obj)

    def test_get_filtered_facilities(self):
        urllib2.urlopen = mock_urlopen
        obj = self.fetcher.get_filtered_facilities(URLS['facility_base_url'], {'updatedSince': '2012-11-16T00:00:00Z'});
        self.assertIsNotNone(obj)

class TestReadFacility(unittest.TestCase):

    def test_process_non_existant_facility(self):
        self.facility = {'id':URLS['test_facility_id2'], 'url':URLS['test_facility_url2']}
        self.reader = ReadFacility(self.facility)
        self.assertFalse(self.reader.does_facility_exists())
        self.assertEquals(self.reader.process_facility(), self.facility)
        self.assertTrue(self.reader.does_facility_exists())

    def test_process_existant_facility(self):
        self.facility = {'id':URLS['test_facility_id'], 'url':URLS['test_facility_url']}
        self.reader = ReadFacility(self.facility)
        HealthFacilityIdMapFactory(uid= self.facility['id'], url = self.facility['url']).save
        self.assertTrue(self.reader.does_facility_exists())
        self.assertEquals(self.reader.process_facility(), self.facility)

def mock_urlopen(request):
    import os
    filedir = os.path.dirname(__file__)
    json_filename = request.get_full_url().rsplit('/',1)[-1].rsplit('?',1)[0]
    path = os.path.join(filedir,'../fixtures/%s' % json_filename)
    jason = open(path).read()
    return MockUrlLibResponse(jason)
