import unittest
import urllib2
from fred_consumer.tests.unit.mock_urllib_response import MockUrlLibResponse
from fred_consumer.fred_connect import Fred_Facilities_Fetcher

CONNECTION_SETTING = {
  'user': 'sekiskylink',
  'password': '123Congse'
}

URLS = {
  'facility_base_url': 'http://ec2-54-242-108-118.compute-1.amazonaws.com/api-fred/v1/facilities',
  'test_facility_url' :'http://ec2-54-242-108-118.compute-1.amazonaws.com/api-fred/v1/facilities/nBDPw7Qhd7r',
  'test_facility_id' : 'nBDPw7Qhd7r'
}

class Test_Facility_Matcher(unittest.TestCase):

    def setUp(self):
        self.fetcher = Fred_Facilities_Fetcher(CONNECTION_SETTING)
        urllib2.urlopen = mock_urlopen


    def test_get(self):
        obj = self.fetcher.get(URLS['facility_base_url']);
        self.assertIsNotNone(obj)

        obj = self.fetcher.get(URLS['test_facility_url'])
        self.assertIsNotNone(obj)

        obj = self.fetcher.get(URLS['test_facility_url'],paging=False);
        self.assertIsNotNone(obj)


    def test_get_facility(self):
        obj = self.fetcher.get_facility(URLS['facility_base_url'],URLS['test_facility_id']);
        self.assertIsNotNone(obj)

    def test_get_filtered_facilities(self):
        obj = self.fetcher.get_filtered_facilities(URLS['facility_base_url'], {'updatedSince': '2012-11-16T00:00:00Z'});
        self.assertIsNotNone(obj)

class Test_Parse_Facility(unittest.TestCase):
    def setUp(self):
        self.fetcher = Fred_Facilities_Fetcher(CONNECTION_SETTING)


    def test_get_facilities(self):
        urllib2.urlopen = mock_urlopen
        facilities = self.fetcher.get(URLS['test_facility_url']);

def mock_urlopen(request):
    import os
    filedir = os.path.dirname(__file__)
    json_filename = request.get_full_url().rsplit('/',1)[-1].rsplit('?',1)[0]
    path = os.path.join(filedir,'../fixtures/%s' % json_filename)
    jason = open(path).read()
    return MockUrlLibResponse(jason)
