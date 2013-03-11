# -*- coding: utf-8 -*-
from lettuce import *
from lxml import html
from django.test.client import Client
from nose.tools import assert_equals
from splinter import Browser
from lettuce.django import django_url
from fred_consumer.models import *
from time import sleep
from random import randint
from datetime import datetime
import reversion, json
from fred_consumer.tasks import *

@transaction.commit_on_success
def create_facility(f):
    f.save(False)
    return f

@before.all
def set_browser():
  world.browser = Browser()
  JobStatus.objects.all().delete()

@after.all
def close_browser(*args):
  facilities = HealthFacility.objects.filter(uuid = "1234").all()
  if facilities:
    facilities.delete()
  world.browser.quit()
  JobStatus.objects.all().delete()

@step(u'Given I am logged in')
def log_in(step):
  visit("/fredconsumer/")
  world.browser.fill("username", "smoke")
  world.browser.fill("password", "password")
  world.browser.find_by_css('input[type=submit]').first.click()

@step(u'Given I am on the Fred landing page')
def access_landing_page(step):
  visit("/fredconsumer/")

@step(u'Then I should see all the fields')
def validate_landing_page_fields(step):
  assert world.browser.is_text_present("FRED Sync", wait_time=3)
  assert world.browser.is_text_present("Failures")

@step(u'And I am on the Fred landing page')
def and_i_am_on_the_fred_landing_page(step):
  visit("/fredconsumer/")

@step(u'Given I have no previous job')
def flush_job_status(step):
  JobStatus.objects.all().delete()

@step(u'And I start a job')
def run_job(step):
  assert world.browser.is_text_present("Sync Now", wait_time=3)
  world.browser.click_link_by_text('Sync Now')
  assert world.browser.is_text_present("Sync has been scheduled! Refresh in few seconds.")
  visit("/fredconsumer/")

@step(u'Then I should see pending current job with timestamp')
def then_i_should_see_pending_current_job_with_timestamp(step):
  from datetime import datetime
  now = datetime.now()
  timestamp = now.strftime("%B ") + now.strftime("%d, %Y, ").strip("0") + now.strftime("%I:%M").strip("0")
  assert world.browser.is_text_present(timestamp, wait_time=3)

@step(u'I terminate the job')
def terminate_job(step):
  world.browser.click_link_by_text('Terminate job')
  assert world.browser.is_text_present("Sync terminated!")

@step(u'And I should see option to start a job')
def option_for_run_job(step):
  assert world.browser.is_text_present("Sync Now")

@step(u'Given I process a facility')
def given_i_process_a_facility(step):
  facility_json = json.loads('{"facilities":[{"uuid":"1234","name":"Apo","active":true,"href":"http:/example/6VeE8JrylXn","createdAt":"2012-08-14T10:00:07.701+0000","updatedAt":"2013-01-22T15:09:55.543+0000","coordinates":[2.2222,0.1111]}]}')['facilities'][0]

  facility_json['name'] = "Apo" + str(randint(1,9999))
  facility = HealthFacility(name="ThoughtWorks facility", uuid = "1234")
  create_facility(facility)
  reversion.get_for_object(facility).delete()

  facility = HealthFacilityBase.objects.get(uuid="1234")
  assert facility.name != facility_json['name']

  process_facility(facility_json)

  facility = HealthFacilityBase.objects.get(uuid="1234")
  assert facility.name == facility_json['name']

@step(u'Given I process a new facility')
def given_i_process_a_new_facility(step):
    facility_json = json.loads('{"facilities":[{"uuid":"6VeE8JrylXy","name":"Apo","active":true,"href":"http:/example/6VeE8JrylXn","createdAt":"2012-08-14T10:00:07.701+0000","updatedAt":"2013-01-22T15:09:55.543+0000","coordinates":[2.2222,0.1111]}]}')['facilities'][0]

    uuid = facility_json['uuid']
    facility_json['name'] = "Apo" + str(randint(1,9999))

    HealthFacilityIdMap.objects.filter(uuid=uuid).delete()
    HealthFacilityBase.objects.filter(uuid=uuid).delete()

    assert len(HealthFacilityIdMap.objects.filter(uuid=uuid)) == 0
    assert len(HealthFacilityBase.objects.filter(uuid=uuid)) == 0

    process_facility(facility_json)

    facility = HealthFacilityBase.objects.filter(uuid=uuid)[0]
    id_map = HealthFacilityIdMap.objects.filter(uuid=uuid)[0]

    assert id_map.url == facility_json['href']
    assert facility.name == facility_json['name']

@step(u'And I should see new reversion logs for the latest facility')
def and_i_should_see_reversion_logs_for_new_record(step):
  facility = HealthFacilityBase.objects.filter(uuid='6VeE8JrylXy')
  facility = facility[0]
  version_list = reversion.get_for_object(facility)
  assert len(version_list) == 1
  version = version_list[0]
  assert version.revision.comment == UPDATE_COMMENT
  assert version.revision.user == API_USER


@step(u'And I should see reversion logs')
def and_i_should_see_reversion_logs(step):
  facility = HealthFacilityBase.objects.get(uuid="1234")

  version_list = reversion.get_for_object(facility)
  assert len(version_list) == 1
  version = version_list[0]
  assert version.revision.comment == UPDATE_COMMENT
  assert version.revision.user == API_USER

@step(u'Given I have few failures from Fred sync')
def and_i_have_few_failures_from_fred_sync(step):
  Failure.objects.all().delete()
  facility = {'name': 'name'}
  for _ in xrange(15):
    process_facility(facility)

@step(u'And I am on the Fred failures page')
def and_i_am_on_the_fred_failures_page(step):
  visit("/fredconsumer/failures/")

@step(u'Then I should see failures paginated')
def then_i_should_see_failures_paginated(step):
  assert world.browser.is_text_present("Time")
  assert world.browser.is_text_present("Exception")
  assert world.browser.is_text_present("JSON Body")
  assert world.browser.is_text_present("HTTP Action")
  assert world.browser.is_text_present("GET")
  assert world.browser.is_text_present("<Page 1 of 2>")
  world.browser.is_element_present_by_css("a[class=next]", wait_time=3)
  world.browser.find_by_css("a[class=next]").first.click()
  assert world.browser.is_text_present("Time")
  assert world.browser.is_text_present("Exception")
  assert world.browser.is_text_present("JSON Body")
  assert world.browser.is_text_present("HTTP Action")
  assert world.browser.is_text_present("GET")
  assert world.browser.is_text_present("<Page 2 of 2>")

def visit(url):
  world.browser.visit(django_url(url))

def fill_config_values():
  world.browser.fill("url", world.fred_config['url'])
  world.browser.fill("username", world.fred_config['username'])
  world.browser.fill("password", world.fred_config['password'])
  world.browser.find_by_id('update').first.click()
