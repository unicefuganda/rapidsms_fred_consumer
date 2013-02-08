from lettuce import *
from fred_consumer.fred_connect import * 
from urllib2 import HTTPError

credentials = {
  'username':"api",
  'password':"P@ssw0rd",
  'url'     :"http://dhis/api-fred/v1/facilities.json"}
connector = FredFacilitiesFetcher(credentials)

@step(u'Given I have created a facility')
def given_i_have_created_a_facility(step):
  connector.write(credentials['url'], {
    'id'  :"foo",
    'name':"bar"})
  assert False, 'This step must be implemented'

@step(u'Given I try to create an invalid facility')
def given_i_try_to_create_an_invalid_facility(step):
  try:
    connector.write(credentials['url'], {'name':"Invalid facility"})
  except HTTPError as error:
    world.lastError = error 

@step(u'Then an error is returned')
def then_an_error_is_returned(step):
  assert not(world.lastError == None)
