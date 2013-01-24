# -*- coding: utf-8 -*-
from lettuce import *
from lxml import html
from django.test.client import Client
from nose.tools import assert_equals
from splinter import Browser
from lettuce.django import django_url
from mtrack_project.rapidsms_fred_consumer.fred_consumer.models import *
from time import sleep
from random import randint

@before.all
def set_browser():
  world.browser = Browser()

@after.all
def close_browser(*args):
  world.browser.quit()
  FredConfig.objects.all().delete()

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
  generate_config_values()
  fill_config_values()

@step(u'And I should see success message')
def verify_success_message(step):
  assert world.browser.is_text_present("Configurations updated successfully!")

@step(u'And I change the configurations')
def update_configrations(step):
  add_new_configration(step)

def visit(url):
  world.browser.visit(django_url(url))

def generate_config_values():
  number = str(randint(1,9999))
  world.fred_config = {
    'url': "http://fred-provider.com/" + number,
    'username': "django" + number,
    'password': "django" + number,
  }

def fill_config_values():
  world.browser.fill("url", world.fred_config['url'])
  world.browser.fill("username", world.fred_config['username'])
  world.browser.fill("password", world.fred_config['password'])
  world.browser.find_by_id('update').first.click()