from django.test import TestCase
from django.core import management
from fred_consumer.models import *
from django.db import IntegrityError
from time import sleep

class TestFredConfig(TestCase):

  def test_uniqueness_on_key(self):
    config = FredConfig.objects.create(key="KEY", value="VALUE")
    self.failUnless(config.id)

    new_config = FredConfig()
    new_config.key = "KEY"
    new_config.value = "VALUE"
    self.failUnlessRaises(IntegrityError, new_config.save)

  def test_get_fred_configs(self):
    url = "http://fred-provider.com/api/v1/"
    username = "django"
    password = "django"
    assert FredConfig.get_fred_configs() == {"url": "", "username": "", "password": ""}
    FredConfig.objects.create(key=FredConfig.URL_KEY      , value=url)
    FredConfig.objects.create(key=FredConfig.USERNAME_KEY , value=username)
    FredConfig.objects.create(key=FredConfig.PASSWORD_KEY , value=password)
    assert FredConfig.get_fred_configs() == {"url": url, "username": username, "password": password}

  def test_store_fred_configs(self):
    url = "http://fred-provider.com/api/v1/"
    username = "django"
    password = "django"
    params = {"url": url, "username": username, "password": password}
    FredConfig.store_fred_configs(params)
    assert FredConfig.get_fred_configs() == params

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
    assert status.time > initial_time

  def test_succeeded(self):
    status = JobStatus.objects.create(job_id="XXX", status=JobStatus.PENDING)
    status.succeeded(True)

    status = JobStatus.objects.all()[0]
    assert status.status == JobStatus.SUCCESS
    status.succeeded(False)

    status = JobStatus.objects.all()[0]
    assert status.status == JobStatus.FAILED

class TestHealthFacilityIdMap(TestCase):

    def test_updation_on_uid(self):
        uid = "uid"
        url = "url"
        HealthFacilityIdMap.objects.create(uid=uid, url=url)

        self.failUnless(HealthFacilityIdMap.objects.filter(uid=uid)[0])

        HealthFacilityIdMap.objects.create(uid="xxx", url=url)
        self.failUnless(HealthFacilityIdMap.objects.filter(uid="xxx")[0])

        map = HealthFacilityIdMap()
        map.uid = uid

        another_url = "some other url"
        map.url = another_url
        map.save()

        maps = HealthFacilityIdMap.objects.filter(uid=uid)
        assert len(maps) == 1
        print maps[0].uid, maps[0].url
        assert maps[0].url == another_url

    def test_uid_as_primary_key(self):
        uid = "uid"
        url = "url"
        map = HealthFacilityIdMap.objects.create(uid=uid, url=url)
        try:
            map.id
            assert True == False, "ID is the Primary key"
        except AttributeError as e:
            assert True == True
        else:
            assert True == False, "ID is the Primary key"

    def test_store(self):
        uid = "1"
        url = "url"
        map = HealthFacilityIdMap.store(uid,url)
        self.failUnless(HealthFacilityIdMap.objects.filter(uid=uid)[0])
