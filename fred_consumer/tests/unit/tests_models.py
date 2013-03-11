from django.test import TestCase
from django.core import management
from fred_consumer.models import *
from django.db import IntegrityError
from time import sleep
import json

class TestJobStatus(TestCase):
  def test_storage(self):
    status = JobStatus.objects.create(job_id="XXX", status=JobStatus.PENDING)
    self.failUnless(status.id)
    initial_time = status.time
    assert status.job_id == "XXX"
    assert status.status == JobStatus.PENDING
    assert status.time != None
    status.status = JobStatus.SUCCESS
    status.save()

    assert status.job_id == "XXX"
    assert status.status == JobStatus.SUCCESS
    assert status.time == initial_time

  def test_succeeded(self):
    status = JobStatus.objects.create(job_id="XXX", status=JobStatus.PENDING)
    status.succeeded(True)

    status = JobStatus.objects.all()[0]
    assert status.status == JobStatus.SUCCESS
    status.succeeded(False)

    status = JobStatus.objects.all()[0]
    assert status.status == JobStatus.FAILED

class TestHealthFacilityIdMap(TestCase):

    def test_updation_on_uuid(self):
        uuid = "uuid"
        url = "url"
        HealthFacilityIdMap.objects.create(uuid=uuid, url=url)

        self.failUnless(HealthFacilityIdMap.objects.filter(uuid=uuid)[0])

        HealthFacilityIdMap.objects.create(uuid="xxx", url=url)
        self.failUnless(HealthFacilityIdMap.objects.filter(uuid="xxx")[0])

        map = HealthFacilityIdMap()
        map.uuid = uuid

        another_url = "some other url"
        map.url = another_url
        map.save()

        maps = HealthFacilityIdMap.objects.filter(uuid=uuid)
        assert len(maps) == 1
        print maps[0].uuid, maps[0].url
        assert maps[0].url == another_url

    def test_uuid_as_primary_key(self):
        uuid = "uuid"
        url = "url"
        map = HealthFacilityIdMap.objects.create(uuid=uuid, url=url)
        try:
            map.id
            assert True == False, "ID is the Primary key"
        except AttributeError as e:
            assert True == True
        else:
            assert True == False, "ID is the Primary key"

    def test_store(self):
        uuid = "1"
        url = "url"
        map = HealthFacilityIdMap.store(uuid,url)
        self.failUnless(HealthFacilityIdMap.objects.filter(uuid=uuid)[0])

class TestFailures(TestCase):
  def test_storage(self):
    exception = Exception('Failed for whatever reasons')
    failed_json = json.dumps({'name': 'BATMAN'})
    failure = Failure.objects.create(exception=exception, json=failed_json, action = "PUT")
    self.failUnless(failure.id)
    assert failure.time != None