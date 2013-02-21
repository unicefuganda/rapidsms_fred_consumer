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


FRED_CONFIG = {"url": "http://dhis/api-fred/v1///", "username": "api", "password": "P@ssw0rd"}
FIXTURES = os.path.abspath(fred_consumer.__path__[0]) + "/tests/fixtures/cassettes/"

URLS = {
    'test_facility_url'      : FRED_CONFIG['url'] + 'facilities/nBDPw7Qhd7r',
    'test_facility_id'       : 'nBDPw7Qhd7r',
    'test_wrong_facility_id' : 'naDPw7Qhd7B'
}

class TestFredFacilitiesFetcher(TestCase):

    def setUp(self):
        FredConfig.store_fred_configs(FRED_CONFIG)
        self.fetcher = FredFacilitiesFetcher(FredConfig.get_fred_configs())

    def test_get_all_facilities(self):
        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
            obj = self.fetcher.get_all_facilities()
            self.assertIsNotNone(obj)

    def test_get_filtered_facilities(self):
        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
            obj = self.fetcher.get_filtered_facilities({'updatedSince': '2013-01-16T00:00:00Z'});
            self.assertIsNotNone(obj)

    def test_get_facility(self):
        HealthFacilityIdMap.objects.create(uuid = URLS['test_facility_id'], url= URLS['test_facility_url'])
        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
            obj = self.fetcher.get_facility(URLS['test_facility_id'])
            self.assertIsNotNone(obj)

    def test_write_request(self):
        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
            obj = self.fetcher.write(URLS['test_facility_url'], {"name": "BBB", "active": "true", "coordinates": [2.2222,0.1111]},"PUT")
            self.assertEqual(200,obj.getcode())

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
      facility_json = json.loads('{"facilities":[{"id":"6VeE8JrylXn","name":" BATMAN HC II","active":true,"url":"http://dhis/api-fred/v1/facilities/6VeE8JrylXn","createdAt":"2012-08-14T10:00:07.701+0000","updatedAt":"2013-01-22T15:09:55.543+0000","coordinates":[2.2222,0.1111],"properties":{"level":1,"hierarchy":[{"id":"OwhPJYQ9gqM","level":1,"name":"MOH-Uganda","url":"http://dhis/api/organisationUnitLevels/OwhPJYQ9gqM"},{"id":"V9O2FgyImDt","level":2,"name":"Region","url":"http://dhis/api/organisationUnitLevels/V9O2FgyImDt"},{"id":"a1XiGwfbe81","level":3,"name":"District","url":"http://dhis/api/organisationUnitLevels/a1XiGwfbe81"},{"id":"fgJNYG1Ps13","level":4,"name":"Sub-County","url":"http://dhis/api/organisationUnitLevels/fgJNYG1Ps13"},{"id":"G5kUCanhxGU","level":5,"name":"Health Unit","url":"http://dhis/api/organisationUnitLevels/G5kUCanhxGU"}]}}]}')['facilities'][0]

      uuid = facility_json['id']
      HealthFacilityType.objects.filter(name="hcii").delete()
      HealthFacilityBase.objects.filter(uuid=uuid).delete()

      HealthFacilityType.objects.create(name="hcii")

      facility = HealthFacilityBase(uuid=uuid, name="BATMAN")
      facility.save(cascade_update=False)
      self.failUnless(facility.id)

      assert len(HealthFacilityIdMap.objects.filter(uuid=uuid)) == 0
      assert len(HealthFacilityBase.objects.filter(uuid=uuid)) == 1

      fred_consumer.tasks.process_facility(facility_json)

      facility = HealthFacilityBase.objects.filter(uuid=uuid)[0]
      self.failUnless(facility)
      self.failUnless(HealthFacilityIdMap.objects.filter(uuid=uuid)[0])
      assert facility.name == "BATMAN HC II"

    def test_process_facility_failures(self):
      facility = {'name': 'name'}
      assert len(Failure.objects.all()) == 0
      fred_consumer.tasks.process_facility(facility)
      assert len(Failure.objects.all()) == 1
      failure = Failure.objects.all()[0]
      assert failure.exception == "KeyError:'id'"
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
            fetcher = FredFacilitiesFetcher(FredConfig.get_fred_configs())
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
            fetcher = FredFacilitiesFetcher(FredConfig.get_fred_configs())
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
            fetcher = FredFacilitiesFetcher(FredConfig.get_fred_configs())
            updated_facility = fetcher.get_facility(URLS['test_facility_id'])
            assert updated_facility['name'] != facility.name

    @patch('fred_consumer.fred_connect.FredFacilitiesFetcher.update_facilities_in_provider')
    def test_send_facility_update_http_failure(self, mock_update_facilities_in_provider):
        assert len(Failure.objects.all()) == 0
        facility = HealthFacility(name = "initial name", uuid= URLS['test_facility_id'])
        facility.save(cascade_update=False)
        facility.name = "new name"
        HealthFacilityIdMap.objects.create(url= URLS['test_facility_url'], uuid=URLS['test_facility_id'])
        mock_update_facilities_in_provider.side_effect = Exception('HTTP ERROR')
        FredFacilitiesFetcher.send_facility_update(facility)
        assert mock_update_facilities_in_provider.called
        assert len(Failure.objects.all()) == 1
        failure = Failure.objects.all()[0]
        assert failure.exception == "Exception:HTTP ERROR"
        facility_json = { 'name': 'new name', 'uuid': URLS['test_facility_id'] }
        assert failure.json == json.dumps(facility_json)
        assert failure.action == "PUT"

    def test_send_facility_update_facility_doesnt_exist_failure(self):
        assert len(Failure.objects.all()) == 0
        facility = HealthFacility(name = "new name", uuid= URLS['test_facility_id'])
        facility.save(cascade_update=False)
        FredFacilitiesFetcher.send_facility_update(facility)
        assert len(Failure.objects.all()) == 1
        failure = Failure.objects.all()[0]
        assert failure.exception == "DoesNotExist:HealthFacilityIdMap matching query does not exist."
        facility_json = { 'name': 'new name', 'uuid': URLS['test_facility_id'] }
        assert failure.json == json.dumps(facility_json)
        assert failure.action == "PUT"

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
        assert failure.exception == 'HTTPError:{"name":"length must be between 2 and 160"}'
        assert failure.action == "POST"
        assert failure.json == '{"active": true, "name": "", "coordinates": [0, 0]}'
