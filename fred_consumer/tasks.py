from celery import Celery, current_task
from fred_consumer.models import *
from healthmodels.models.HealthFacility import *
from fred_consumer.fred_connect import *
from django.contrib.auth.models import User
import re
import reversion
from django.db import transaction

celery = Celery()
FACILITY_TYPE_MAP = {
                      'HC IV'             : 'hciv',
                      'HC III'            : 'hciii',
                      'HC II'             : 'hcii',
                      'Hospital'          : 'hospital',
                      'HOSPITAL'          : 'hospital',
                    }
API_USER = User.objects.get(id=-1)
UPDATE_COMMENT = "Updated name field from DHIS2."

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
  fetcher = FredFacilitiesFetcher(FredConfig.get_fred_configs())
  fetcher.sync(current_task.request.id)

@celery.task
def process_facility(facility):
  try:
    uuid = facility['id']
    name = facility['name']
    HealthFacilityIdMap.store(uuid, facility['url'])
    existing_facility = HealthFacilityBase.objects.filter(uuid=uuid)
    if existing_facility:
      facility = existing_facility[0]
    else:
      create_facility(uuid)
      facility = HealthFacilityBase.objects.get(uuid=uuid)
    facility.name = name.strip()
    with reversion.create_revision():
        facility.save(cascade_update=False)
        reversion.set_user(API_USER)
        reversion.set_comment(UPDATE_COMMENT)
  except Exception, e:
    exception = type(e).__name__ +":"+ str(e)
    Failure.objects.create(exception=exception, json=facility)
