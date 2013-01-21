
import unittest
import get_fred_facility
import datetime


CONNECTION_SETTING = {
    'user': 'sekiskylink',
    'password': '123Congse'
}

URLS = {
    'facility_base_url': 'http://localhost:8080/dhis2/api-fred/v1/facilities',
    'test_facility_url' :'http://localhost:8080/dhis2/api-fred/v1/facilities/nBDPw7Qhd7r',
    'test_facility_id' : 'nBDPw7Qhd7r'
}

class Test_Facility_Matcher(unittest.TestCase):

    def setUp(self):
        print "-----------------------------------"
        print "Running test for fred consumer"
        self.fetcher = get_fred_facility.Fred_Facilities_Fetcher(CONNECTION_SETTING)

        def test_get(self):
            obj = self.fetcher.get(URLS['facility_base_url']);
            self.assertNotEqual(obj,None)

            obj = self.fetcher.get(URLS['test_facility_url']);
            self.assertNotEqual(obj,None)

            obj = self.fetcher.get(URLS['test_facility_url'],paging=False);
            self.assertNotEqual(obj,None)

        def test_get_facility(self):
            obj = self.fetcher.get_facility(URLS['facility_base_url'],URLS['test_facility_id']);
            self.assertNotEqual(obj,None)

    def test_get_filtered_facilities(self):
        obj = self.fetcher.get_filtered_facilities(URLS['facility_base_url'], {'updatedSince': '2012-11-16T00:00:00Z'});
        print obj['facilities'][0]['id']
        self.assertNotEqual(obj,None)

if __name__ == '__main__':
    unittest.main()
