from celery import Celery, current_task
from fred_consumer.models import *
from healthmodels.models.HealthFacility import *
from fred_consumer.fred_connect import *
from django.contrib.auth.models import User
import re
import reversion
from django.db import transaction
from rapidsms.contrib.locations.models import Location

celery = Celery()
FACILITY_TYPE_MAP = {
                      'HC IV'             : 'hciv',
                      'HC III'            : 'hciii',
                      'HC II'             : 'hcii',
                      'Hospital'          : 'hospital',
                      'HOSPITAL'          : 'hospital',
                    }
API_USER = User.objects.get(id=-1)
UPDATE_COMMENT = "Updated by FRED changes."

def find_facility_type(text):
    rc = re.compile('|'.join(map(re.escape, FACILITY_TYPE_MAP.keys())), re.IGNORECASE)
    result = re.findall(rc, text)
    return FACILITY_TYPE_MAP[result[-1]]

@transaction.commit_on_success
def create_facility(uuid):
    facility = HealthFacility(uuid=uuid)
    facility.save(cascade_update=False)

@celery.task
def run_fred_sync():
    fetcher = FredFacilitiesFetcher(FredConfig.get_settings())
    fetcher.sync(current_task.request.id)

def add_catchment_area(facility_json, facility):
    fetcher = FredFacilitiesFetcher(FredConfig.get_settings())
    location_hash = fetcher.get_locations_for_facility(facility_json['properties']['parent'])
    district = Location.objects.filter(name=location_hash["district"], type = "district")[0]
    subcounty = Location.objects.filter(name=location_hash["subcounty"], type = "sub_county", parent_id = district.id)
    if subcounty:
        existing_catchment_areas = set(facility.catchment_areas.all())
        existing_catchment_areas.update(subcounty)
        facility.catchment_areas = list(existing_catchment_areas)
        facility.save(cascade_update=False)

@celery.task
def process_facility(facility_json):
  try:
    facility_json['name'] = facility_json['name'].strip()
    HealthFacilityIdMap.store(facility_json['uuid'], facility_json['href'])
    facility = HealthFacilityBase.store_json(facility_json, comment = UPDATE_COMMENT, cascade_update = False)
    if facility_json["properties"].has_key("dataSets"):
        add_catchment_area(facility_json, facility)
  except Exception, e:
    exception = type(e).__name__ +":"+ str(e)
    Failure.objects.create(exception=exception, json=facility_json)
