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
import time

@before.all
def set_browser():
  world.browser = Browser()
  FredConfig.objects.all().delete()
  JobStatus.objects.all().delete()

@after.all
def close_browser(*args):
  world.browser.quit()
  FredConfig.objects.all().delete()
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
  assert world.browser.is_text_present("FRED Settings")
  assert world.browser.is_text_present("Failures")
  assert world.browser.is_text_present("Provider URL")
  assert world.browser.is_text_present("Username")
  assert world.browser.is_text_present("Password")

@step(u'Given I have my fred settings added')
def load_fred_settings(step):
  world.fred_config = {
    'url'     : FredConfig.objects.create(key=FredConfig.URL_KEY      , value="http://fred-provider.com/api/v1/"),
    'username': FredConfig.objects.create(key=FredConfig.USERNAME_KEY , value="django"),
    'password': FredConfig.objects.create(key=FredConfig.PASSWORD_KEY , value="django"),
  }

@step(u'And I am on the Fred landing page')
def and_i_am_on_the_fred_landing_page(step):
  visit("/fredconsumer/")

@step(u'Then I should see all the fields populated with values')
def validate_landing_page_fields_populated(step):
  assert world.browser.find_by_id('fred_url')[0].value      == world.fred_config['url'].value
  assert world.browser.find_by_id('fred_username')[0].value == world.fred_config['username'].value
  assert world.browser.find_by_id('fred_password')[0].value == world.fred_config['password'].value

@step(u'Given I have no configurations stored')
def flush_configurations(step):
  FredConfig.objects.all().delete()

@step(u'And I enter new configurations')
def add_new_configration(step):
  number = str(randint(1,9999))
  world.fred_config = {
    'url': "http://dhis/api-fred/v1/" + number,
    'username': "api" + number,
    'password': "P@ssw0rd" + number,
  }
  fill_config_values()

@step(u'And I should see success message')
def verify_success_message(step):
  assert world.browser.is_text_present("Configurations updated successfully!")

@step(u'And I change the configurations')
def update_configrations(step):
  world.fred_config = {
    'url': "http://dhis/api-fred/v1/",
    'username': "api",
    'password': "P@ssw0rd",
  }
  fill_config_values()

@step(u'Given I have no previous job')
def flush_job_status(step):
  JobStatus.objects.all().delete()

@step(u'And I start a job')
def run_job(step):
  world.browser.click_link_by_text('Sync Now')
  assert world.browser.is_text_present("Sync has been scheduled! Refresh in few seconds.")
  visit("/fredconsumer/")

@step(u'Then I should see pending current job with timestamp')
def then_i_should_see_pending_current_job_with_timestamp(step):
  now = datetime.now()
  timestamp = now.strftime("%b. ") + now.strftime("%d, %Y, ").strip("0") + now.strftime("%I:%M").strip("0")
  assert world.browser.is_text_present(timestamp)

@step(u'I terminate the job')
def terminate_job(step):
  world.browser.click_link_by_text('Terminate job')
  assert world.browser.is_text_present("Sync terminated!")

@step(u'And I should see option to start a job')
def option_for_run_job(step):
  assert world.browser.is_text_present("Sync Now")

def visit(url):
  world.browser.visit(django_url(url))

def fill_config_values():
  world.browser.fill("url", world.fred_config['url'])
  world.browser.fill("username", world.fred_config['username'])
  world.browser.fill("password", world.fred_config['password'])
  world.browser.find_by_id('update').first.click()