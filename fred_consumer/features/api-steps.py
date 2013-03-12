from lettuce import *
from fred_consumer.fred_connect import * 
from urllib2 import HTTPError
import random
import string

credentials = FredConfig.get_fred_configs()
connector = FredFacilitiesFetcher(credentials)

def new_name():
  return ''.join(random.choice(string.letters) for i in xrange(15))

@step(u'Given I have created a facility')
def given_i_have_created_a_facility(step):
  world.name = "Facility " + new_name() 
  connector.write(credentials['url'], {
    'name'       : world.name, 
    'active'     : True,
    'coordinates': [0,0]})

@step(u'Then it should appear at the top of the feed')
def then_it_should_appear_at_the_top_of_the_feed (step):
    facilities = connector.get_json(".json")['facilities']
    names = map(lambda facility: facility['name'], facilities)
    world.facility = facilities[names.index(world.name)]
    assert world.name == world.facility['name'] 

@step(u'Then I should be able to read it')
def then_i_should_be_able_to_read_it (step):
    facility = connector.get_json(".json", world.facility['url'])
    assert world.facility['name'] == facility['name']

@step(u'And I should be able to update it')
def and_i_should_be_able_to_update_it (step):
    name = new_name()
    world.facility['name'] = name
    connector.write(world.facility['url'], world.facility, "PUT")
    facility = connector.get_json(".json", world.facility['url'])
    assert world.facility['name'] == facility['name']

@step(u'Given I try to create an invalid facility')
def given_i_try_to_create_an_invalid_facility(step):
  try:
    connector.write(credentials['url'], {'name':"Invalid facility"})
  except HTTPError as error:
    world.lastResponse = error.code

@step(u'Then an error is returned')
def then_an_error_is_returned(step):
  assert world.lastResponse == 422 
