from django.test import TestCase
import urllib2
from fred_consumer.tests.unit.mock_urllib_response import MockUrlLibResponse
from fred_consumer.fred_connect import *
from fred_consumer.models import *
import vcr, sys, os, fred_consumer
from healthmodels.models.HealthFacility import HealthFacilityBase, HealthFacilityType
from mock import *
from fred_consumer.tasks import *
import json
from rapidsms.contrib.locations.models import Location

FRED_CONFIG = FredConfig.get_settings()

FIXTURES = os.path.abspath(fred_consumer.__path__[0]) + "/tests/fixtures/cassettes/"

URLS = {
    'test_facility_url'      : FRED_CONFIG['url'] + 'facilities/nBDPw7Qhd7r',
    'test_facility_id'       : 'nBDPw7Qhd7r',
    'test_wrong_facility_id' : 'naDPw7Qhd7B'
}

class TestFredFacilitiesFetcher(TestCase):

    def setUp(self):
        self.fetcher = FredFacilitiesFetcher(FredConfig.get_settings())

    def test_connect_to_fred_strips_slashes(self):
        fred_config = {'url': u'http://example////', 'username': '', 'password': '', "dhis_org_unit_url": "dhis_org_unit_url"}
        self.fetcher = FredFacilitiesFetcher(fred_config)
        assert self.fetcher.BASE_URL == 'http://example'

    def test_get_all_facilities(self):
        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
            obj = self.fetcher.get_all_facilities()
            self.assertIsNotNone(obj)

    def test_get_all_facilities_calls_with_limit(self):
        self.fetcher.get_json = MagicMock(return_value={"facilities":[]})
        obj = self.fetcher.get_all_facilities()

        self.fetcher.get_json.assert_called_with(url=FRED_CONFIG['url'].strip("/") + "/facilities", query='limit=off', extension='.json')

    def test_get_filtered_facilities(self):
        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
            obj = self.fetcher.get_filtered_facilities({'updatedSince': '2013-01-16T00:00:00Z'});
            self.assertIsNotNone(obj)

    def test_get_facility(self):
        HealthFacilityIdMap.objects.create(uuid = URLS['test_facility_id'], url= URLS['test_facility_url'])
        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
            obj = self.fetcher.get_facility(URLS['test_facility_id'])
            self.assertIsNotNone(obj)

    @patch('fred_consumer.tasks.process_facility.delay')
    def test_sync(self, mock_process_facility):
      with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/test_get_all_facilities.yaml"):
        assert len(JobStatus.objects.all()) == 0
        self.fetcher.sync("JOB ID")
        assert JobStatus.objects.all()[0].status == JobStatus.SUCCESS
        assert mock_process_facility.called

    def test_sync_failed(self):
      self.fetcher.fetch_facilities = MagicMock(side_effect=Exception('Boom!'))
      assert len(JobStatus.objects.all()) == 0
      self.fetcher.sync("JOB ID")
      assert JobStatus.objects.all()[0].status == JobStatus.FAILED

    @patch('fred_consumer.tasks.process_facility.delay')
    def test_sync_with_filters(self, mock_process_facility):
      status = JobStatus.objects.create(job_id="XXX", status=JobStatus.SUCCESS)
      self.fetcher.get_filtered_facilities = MagicMock(return_value={"facilities":[]})
      self.fetcher.sync("JOB ID")
      self.fetcher.get_filtered_facilities.assert_called_once_with({'updatedSince': status.time.strftime("%Y-%m-%dT%H:%M:%SZ")})
      assert mock_process_facility.called == False

    def test_process_facility(self):
      facility_json = json.loads('{  "uuid": "18a021ed-205c-4e80-ab9c-fbeb2d9c1bcf",  "name": " Some HOSPITAL",  "active": false,  "href": "http://dhis/api-fred/v1/facilities/123",  "createdAt": "2013-01-15T11:14:02.863+0000",  "updatedAt": "2013-01-15T11:14:02.863+0000",  "coordinates": [34.19622, 0.70331],  "identifiers": [{    "agency": "DHIS2",    "context": "DHIS2_UID",    "id": "123"  }],  "properties": {    "dataSets": ["123456"],    "level": 5,    "ownership": "Private Not For Profit",    "parent": "56789",    "type": "General Hospital"  }}')

      uuid = facility_json['uuid']
      HealthFacilityType.objects.filter(name="hcii").delete()
      HealthFacilityBase.objects.filter(uuid=uuid).delete()

      HealthFacilityType.objects.create(name="hcii")

      facility = HealthFacilityBase(uuid=uuid, name="BATMAN")
      facility.save(cascade_update=False)
      self.failUnless(facility.id)

      assert facility.active == True

      assert len(HealthFacilityIdMap.objects.filter(uuid=uuid)) == 0
      assert len(HealthFacilityBase.objects.filter(uuid=uuid)) == 1

      fred_consumer.tasks.process_facility(facility_json)

      facility = HealthFacilityBase.objects.filter(uuid=uuid)[0]
      self.failUnless(facility)
      self.failUnless(HealthFacilityIdMap.objects.filter(uuid=uuid)[0])
      assert facility.name == facility_json['name'].strip()
      assert facility.active == False

      fred_facility_details = FredFacilityDetail.objects.get(uuid=facility_json['uuid'])
      assert fred_facility_details.h033b == False

    def test_process_facility_create(self):
        facility_json = json.loads('{  "uuid": "18a021ed-205c-4e80-ab9c-fbeb2d9c1bcf",  "name": " Some HOSPITAL",  "active": true,  "href": "http://dhis/api-fred/v1/facilities/123",  "createdAt": "2013-01-15T11:14:02.863+0000",  "updatedAt": "2013-01-15T11:14:02.863+0000",  "coordinates": [34.19622, 0.70331],  "identifiers": [{    "agency": "DHIS2",    "context": "DHIS2_UID",    "id": "123"  }],  "properties": {    "dataSets": ["V1kJRs8CtW4"],    "level": 5,    "ownership": "Private Not For Profit",    "parent": "56789",    "type": "General Hospital"  }}')
        uuid = facility_json['uuid']
        HealthFacilityType.objects.filter(name="hcii").delete()
        HealthFacilityBase.objects.filter(uuid=uuid).delete()

        assert len(HealthFacilityIdMap.objects.filter(uuid=uuid)) == 0
        assert len(HealthFacilityBase.objects.filter(uuid=uuid)) == 0

        fred_consumer.tasks.process_facility(facility_json)

        facility = HealthFacilityBase.objects.filter(uuid=uuid)[0]
        self.failUnless(facility)
        self.failUnless(HealthFacilityIdMap.objects.filter(uuid=uuid)[0])
        assert facility.name == facility_json['name'].strip()
        assert facility.active == True

        fred_facility_details = FredFacilityDetail.objects.get(uuid=facility_json['uuid'])
        assert fred_facility_details.h033b == True

    def test_process_facility_failures(self):
      facility = {'name': 'name'}
      assert len(Failure.objects.all()) == 0
      fred_consumer.tasks.process_facility(facility)
      assert len(Failure.objects.all()) == 1
      failure = Failure.objects.all()[0]
      assert failure.exception == "KeyError:'uuid'"
      assert failure.json == "{'name': 'name'}"

    @patch('fred_consumer.fred_connect.FredFacilitiesFetcher.sync')
    def test_sync_task(self, mocked_sync):
      fred_consumer.tasks.run_fred_sync()
      assert mocked_sync.called

    def test_send_facility_update_without_etag(self):
        facility = HealthFacility(name = "new name", uuid= URLS['test_facility_id'])
        facility.save(cascade_update=False)
        HealthFacilityIdMap.objects.create(url= URLS['test_facility_url'], uuid=URLS['test_facility_id'])
        facility_json = { 'name': facility.name }

        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + "-get.yaml"):
            response = self.fetcher.get("/facilities/" + facility.uuid + ".json")
            response.info().getheader = MagicMock(return_value = None)

        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + "-put.yaml"):
            self.fetcher.get = MagicMock(return_value = response)
            self.fetcher.update_facilities_in_provider(facility.uuid, facility_json)

        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + "-updated-get.yaml"):
            fetcher = FredFacilitiesFetcher(FredConfig.get_settings())
            updated_facility = fetcher.get_facility(URLS['test_facility_id'])
            self.assertEqual(updated_facility['name'], facility.name)

    def test_send_facility_update_with_etag(self):
        facility = HealthFacility(name = "new name", uuid= URLS['test_facility_id'])
        facility.save(cascade_update=False)
        HealthFacilityIdMap.objects.create(url= URLS['test_facility_url'], uuid=URLS['test_facility_id'])
        facility_json = { 'name': facility.name }

        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
            self.fetcher.update_facilities_in_provider(facility.uuid, facility_json)

        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + "-updated-get.yaml"):
            fetcher = FredFacilitiesFetcher(FredConfig.get_settings())
            updated_facility = fetcher.get_facility(URLS['test_facility_id'])
            self.assertEqual(updated_facility['name'], facility.name)

    def test_send_facility_update_failure_with_etag(self):
        facility = HealthFacility(name = "new name 12345", uuid= URLS['test_facility_id'])
        facility.save(cascade_update=False)
        HealthFacilityIdMap.objects.create(url= URLS['test_facility_url'], uuid=URLS['test_facility_id'])
        facility_json = { 'name': facility.name }

        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + "-get.yaml"):
            response = self.fetcher.get("/facilities/" + facility.uuid + ".json")
            response.info().getheader = MagicMock(return_value = "Rajini")

        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + "-put.yaml"):
            self.fetcher.get = MagicMock(return_value = response)
            try:
                self.fetcher.update_facilities_in_provider(facility.uuid, facility_json)
                assert True == False, "Call Succeeded"
            except Exception, e:
                assert str(e) == "HTTP Error 412: Precondition Failed"

        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + "-updated-get.yaml"):
            fetcher = FredFacilitiesFetcher(FredConfig.get_settings())
            updated_facility = fetcher.get_facility(URLS['test_facility_id'])
            assert updated_facility['name'] != facility.name

    def test_send_facility_update_http_failure(self):
        assert len(Failure.objects.all()) == 0
        facility = HealthFacility(name = "initial name", uuid= URLS['test_facility_id'])
        facility.save(cascade_update=False)
        facility.name = ""
        HealthFacilityIdMap.objects.create(url= URLS['test_facility_url'], uuid=URLS['test_facility_id'])

        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
            assert FredFacilitiesFetcher.send_facility_update(facility) == False

        assert len(Failure.objects.all()) == 1
        failure = Failure.objects.all()[0]
        assert failure.exception == 'HTTPError:{"name":"length must be between 2 and 160"}:%s.json' % URLS['test_facility_url']

        failure_json = json.loads(failure.json)
        assert failure_json["name"] == facility.name
        assert failure_json["href"] == URLS['test_facility_url'].strip("/")
        assert failure.action == "PUT"

    def test_send_facility_update_facility_doesnt_exist_failure(self):
        assert len(Failure.objects.all()) == 0
        facility = HealthFacility(name = "new name", uuid= URLS['test_facility_id'])
        facility.save(cascade_update=False)
        FredFacilitiesFetcher.send_facility_update(facility)
        assert len(Failure.objects.all()) == 1
        failure = Failure.objects.all()[0]
        assert failure.exception == "DoesNotExist:HealthFacilityIdMap matching query does not exist."
        facility_json = { 'name': 'new name', 'uuid': URLS['test_facility_id'], 'active': True}
        assert failure.json == json.dumps(facility_json)
        assert failure.action == "GENERIC"

    def test_create_facility(self):
        facility = HealthFacility(name = "new name")
        facility_json = {'name': facility.name,
                         'active': True,
                         'coordinates': [0,0]
        }
        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
            facility.save()

        self.failUnless(facility.id)
        self.failUnless(facility.uuid)
        facility_in_fred = HealthFacilityIdMap.objects.get(uuid = str(facility.uuid))
        self.failUnless(facility_in_fred.url)

    def test_create_facility_failure(self):
        facility = HealthFacility()

        assert len(Failure.objects.all()) == 0
        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + "-post.yaml"):
            self.failUnlessRaises(ValidationError, facility.save)

        assert len(Failure.objects.all()) == 1
        failure = Failure.objects.all()[0]
        assert failure.exception == 'HTTPError:{"name":"length must be between 2 and 160"}:http://dhis/api-fred/v1/facilities.json'
        assert failure.action == "POST"
        assert failure.json == '{"active": true, "name": "", "coordinates": [0, 0]}'

    def test_create_facility_non_http_failure(self):
        facility = HealthFacility(name = "new name")
        facility_json = {'name': facility.name,
                         'active': True,
                         'coordinates': [0,0]
        }
        assert len(Failure.objects.all()) == 0
        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
            self.failUnlessRaises(ValidationError, facility.save)

        assert len(Failure.objects.all()) == 1
        failure = Failure.objects.all()[0]
        assert failure.exception == "KeyError:'uuid'"
        assert failure.json == json.dumps({"active": True, "name": "new name", "coordinates": [0, 0]})
        assert failure.action == "GENERIC"

    def test_get_locations_for_facility(self):
        parent_id = "y1iun1mJXWa"
        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + "-get.yaml"):
            location = self.fetcher.get_locations_for_facility(parent_id)
        assert location["subcounty"] == "Usuk"
        assert location["district"] == "Katakwi"

    def test_process_facility_create_with_catchment_area(self):
        facility_json = json.loads('{  "uuid": "18a021ed-205c-4e80-ab9c-fbeb2d9c1bcf",  "name": " Some HOSPITAL",  "active": true,  "href": "http://dhis/api-fred/v1/facilities/123",  "createdAt": "2013-01-15T11:14:02.863+0000",  "updatedAt": "2013-01-15T11:14:02.863+0000",  "coordinates": [34.19622, 0.70331],  "identifiers": [{    "agency": "DHIS2",    "context": "DHIS2_UID",    "id": "123"  }],  "properties": {    "dataSets": ["V1kJRs8CtW4"],    "level": 5,    "ownership": "Private Not For Profit",    "parent": "y1iun1mJXWa",    "type": "General Hospital"  }}')
        uuid = facility_json['uuid']
        HealthFacilityType.objects.filter(name="hcii").delete()
        HealthFacilityBase.objects.filter(uuid=uuid).delete()
        district = Location.objects.create(name="Katakwi", type_id = "district")
        county = Location.objects.create(name="Some county", type_id = "parish")
        county.set_parent(district)
        sub_county = Location.objects.create(name="Usuk", type_id = "sub_county")
        sub_county.set_parent(county)

        assert len(HealthFacilityIdMap.objects.filter(uuid=uuid)) == 0
        assert len(HealthFacilityBase.objects.filter(uuid=uuid)) == 0

        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
            fred_consumer.tasks.process_facility(facility_json)

        facility = HealthFacilityBase.objects.filter(uuid=uuid)[0]
        self.failUnless(facility)
        self.failUnless(HealthFacilityIdMap.objects.filter(uuid=uuid)[0])
        assert facility.name == facility_json['name'].strip()
        assert facility.active == True

        fred_facility_details = FredFacilityDetail.objects.get(uuid=facility_json['uuid'])
        assert fred_facility_details.h033b == True

        catchment_areas = facility.catchment_areas.all()
        assert len(catchment_areas) == 1
        print catchment_areas
        assert catchment_areas[0].name == "Usuk"

        facility = HealthFacilityBase.objects.filter(uuid=uuid)[0]
        facility.catchment_areas = [district, sub_county, county]
        facility.save(cascade_update = False)

        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
            fred_consumer.tasks.process_facility(facility_json)

        facility = HealthFacilityBase.objects.filter(uuid=uuid)[0]
        catchment_areas = facility.catchment_areas.all()
        assert len(catchment_areas) == 3
        assert facility.district == district.name

    def test_process_facility_which_is_not_a_facility(self):
        facility_json = json.loads('{  "uuid": "18a021ed-205c-4e80-ab9c-fbeb2d9c1bcf",  "name": " Some HOSPITAL",  "active": true,  "href": "http://dhis/api-fred/v1/facilities/123",  "createdAt": "2013-01-15T11:14:02.863+0000",  "updatedAt": "2013-01-15T11:14:02.863+0000",  "coordinates": [34.19622, 0.70331],  "identifiers": [{    "agency": "DHIS2",    "context": "DHIS2_UID",    "id": "123"  }],  "properties": {    "level": 5,    "ownership": "Private Not For Profit",    "parent": "y1iun1mJXWa",    "type": "General Hospital"  }}')
        uuid = facility_json['uuid']
        HealthFacilityType.objects.filter(name="hcii").delete()
        HealthFacilityBase.objects.filter(uuid=uuid).delete()

        assert len(HealthFacilityIdMap.objects.filter(uuid=uuid)) == 0
        assert len(HealthFacilityBase.objects.filter(uuid=uuid)) == 0

        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
            fred_consumer.tasks.process_facility(facility_json)

        facility = HealthFacilityBase.objects.filter(uuid=uuid)[0]
        self.failUnless(facility)
        self.failUnless(HealthFacilityIdMap.objects.filter(uuid=uuid)[0])
        assert facility.name == facility_json['name'].strip()
        assert facility.active == True
        assert facility.district == ''

        fred_facility_details = FredFacilityDetail.objects.get(uuid=facility_json['uuid'])
        assert fred_facility_details.h033b == False

        assert len(facility.catchment_areas.all()) == 0

    def test_process_facility_with_location_not_available_in_mtrac(self):
        facility_json = json.loads('{  "uuid": "18a021ed-205c-4e80-ab9c-fbeb2d9c1bcf",  "name": " Some HOSPITAL",  "active": true,  "href": "http://dhis/api-fred/v1/facilities/123",  "createdAt": "2013-01-15T11:14:02.863+0000",  "updatedAt": "2013-01-15T11:14:02.863+0000",  "coordinates": [34.19622, 0.70331],  "identifiers": [{    "agency": "DHIS2",    "context": "DHIS2_UID",    "id": "123"  }],  "properties": {    "dataSets": ["V1kJRs8CtW4"],    "level": 5,    "ownership": "Private Not For Profit",    "parent": "y1iun1mJXWa",    "type": "General Hospital"  }}')
        uuid = facility_json['uuid']
        HealthFacilityType.objects.filter(name="hcii").delete()
        HealthFacilityBase.objects.filter(uuid=uuid).delete()
        district = Location.objects.create(name="Katakwi", type_id = "district")

        assert len(HealthFacilityIdMap.objects.filter(uuid=uuid)) == 0
        assert len(HealthFacilityBase.objects.filter(uuid=uuid)) == 0

        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
            fred_consumer.tasks.process_facility(facility_json)

        facility = HealthFacilityBase.objects.filter(uuid=uuid)[0]
        self.failUnless(facility)
        self.failUnless(HealthFacilityIdMap.objects.filter(uuid=uuid)[0])
        assert facility.name == facility_json['name'].strip()
        assert facility.active == True
        assert facility.district == district.name

        fred_facility_details = FredFacilityDetail.objects.get(uuid=facility_json['uuid'])
        assert fred_facility_details.h033b == True

        catchment_areas = facility.catchment_areas.all()
        assert len(catchment_areas) == 1
        assert catchment_areas[0].name == "Katakwi"

        locations = FredFaciltiyLocation.objects.all()
        assert len(locations) == 1
        assert locations[0].subcounty == "Usuk"
        assert locations[0].district == "Katakwi"

    def test_process_facility_with_type_but_no_dataSets(self):
        facility_json = json.loads('{  "uuid": "18a021ed-205c-4e80-ab9c-fbeb2d9c1bcf",  "name": " Some HOSPITAL",  "active": true,  "href": "http://dhis/api-fred/v1/facilities/123",  "createdAt": "2013-01-15T11:14:02.863+0000",  "updatedAt": "2013-01-15T11:14:02.863+0000",  "coordinates": [34.19622, 0.70331],  "identifiers": [{    "agency": "DHIS2",    "context": "DHIS2_UID",    "id": "123"  }],  "properties": {    "level": 5,    "ownership": "Private Not For Profit",    "parent": "y1iun1mJXWa",    "type": "General Hospital"  }}')
        uuid = facility_json['uuid']
        HealthFacilityType.objects.filter(name="hcii").delete()
        HealthFacilityBase.objects.filter(uuid=uuid).delete()
        district = Location.objects.create(name="Katakwi", type_id = "district")

        assert len(HealthFacilityIdMap.objects.filter(uuid=uuid)) == 0
        assert len(HealthFacilityBase.objects.filter(uuid=uuid)) == 0

        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
            fred_consumer.tasks.process_facility(facility_json)

        facility = HealthFacilityBase.objects.filter(uuid=uuid)[0]
        self.failUnless(facility)
        self.failUnless(HealthFacilityIdMap.objects.filter(uuid=uuid)[0])
        assert facility.name == facility_json['name'].strip()
        assert facility.active == True
        assert facility.district == district.name
        

        fred_facility_details = FredFacilityDetail.objects.get(uuid=facility_json['uuid'])
        assert fred_facility_details.h033b == False

        catchment_areas = facility.catchment_areas.all()
        assert len(catchment_areas) == 1
        assert catchment_areas[0].name == "Katakwi"

        locations = FredFaciltiyLocation.objects.all()
        assert len(locations) == 1
        assert locations[0].subcounty == "Usuk"
        assert locations[0].district == "Katakwi"

    def test_process_facility_with_type_but_not_from_dhis2_and_no_dataSets(self):
        facility_json = json.loads('{  "uuid": "18a021ed-205c-4e80-ab9c-fbeb2d9c1bcf",  "name": " Some HOSPITAL",  "active": true,  "href": "http://dhis/api-fred/v1/facilities/123",  "createdAt": "2013-01-15T11:14:02.863+0000",  "updatedAt": "2013-01-15T11:14:02.863+0000",  "coordinates": [34.19622, 0.70331],  "identifiers": [{    "agency": "DHIS2",    "context": "DHIS2_UID",    "id": "123"  }],  "properties": {    "level": 5,    "ownership": "Private Not For Profit",    "parent": "y1iun1mJXWa" }}')
        uuid = facility_json['uuid']
        HealthFacilityBase.objects.filter(uuid=uuid).delete()
        district = Location.objects.create(name="Katakwi", type_id = "district")
        some_type = HealthFacilityType.objects.create()
        HealthFacilityBase.objects.create(name=facility_json['name'], uuid=uuid, type=some_type)

        assert len(HealthFacilityIdMap.objects.filter(uuid=uuid)) == 0

        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
            fred_consumer.tasks.process_facility(facility_json)

        facility = HealthFacilityBase.objects.filter(uuid=uuid)[0]
        self.failUnless(facility)
        self.failUnless(HealthFacilityIdMap.objects.filter(uuid=uuid)[0])
        assert facility.name == facility_json['name'].strip()
        assert facility.active == True
        assert facility.district == district.name

        fred_facility_details = FredFacilityDetail.objects.get(uuid=facility_json['uuid'])
        assert fred_facility_details.h033b == False

        catchment_areas = facility.catchment_areas.all()
        assert len(catchment_areas) == 1
        assert catchment_areas[0].name == "Katakwi"

        locations = FredFaciltiyLocation.objects.all()
        assert len(locations) == 1
        assert locations[0].subcounty == "Usuk"
        assert locations[0].district == "Katakwi"
        

    def test_real_facility_for_facility_json_with_datasets(self):
        facility_json= json.loads('{"properties": {"dataSets":"hahaha"}}')
        assert fred_consumer.tasks.real_facility(facility_json, 'mocked_facility')
    
    def test_real_facility_for_facility_json_with_type(self):
        facility_json= json.loads('{"properties": {"type":"hahaha"}}')
        assert fred_consumer.tasks.real_facility(facility_json, 'mocked_facility')    
        
    def test_real_facility_for_facility_having_a_type_in_mtrac(self):
        facility = MagicMock()
        facility.type = 'not False'
        
        facility_json = json.loads('{"properties": {"no_datasets_or_type":"yes yes yes"} }')
        
        assert fred_consumer.tasks.real_facility(facility_json, facility)        