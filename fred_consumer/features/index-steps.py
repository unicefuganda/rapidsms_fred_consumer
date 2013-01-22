# -*- coding: utf-8 -*-
from lettuce import *
from lxml import html
from django.test.client import Client
from nose.tools import assert_equals
from splinter import Browser
from lettuce.django import django_url
from mtrack_project.rapidsms_fred_consumer.fred_consumer.models import *

@before.all
def set_browser():
  world.browser = Browser()

@after.all
def close_browser(*args):
  world.browser.quit()
  FredConfig.objects.all().delete()

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
  world.fred_config = FredConfig.objects.create(url="http://fred-provider.com/api/v1/", username="django", password="django")

@step(u'And I am on the Fred landing page')
def and_i_am_on_the_fred_landing_page(step):
  visit("/fredconsumer/")

@step(u'Then I should see all the fields populated with values')
def validate_landing_page_fields_populated(step):
  assert world.browser.find_by_id('fred_settings')[0].value == world.fred_config.url
  assert world.browser.find_by_id('fred_username')[0].value == world.fred_config.username
  assert world.browser.find_by_id('fred_password')[0].value == world.fred_config.password

def visit(url):
  world.browser.visit(django_url(url))