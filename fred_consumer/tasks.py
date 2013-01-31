from celery import Celery, current_task
from fred_consumer.models import *
from healthmodels.models.HealthFacility import *
from fred_consumer.fred_connect import *
import re

celery = Celery()
FACILITY_TYPE_MAP = {
                      'HC IV'             : 'hciv',
                      'HC III'            : 'hciii',
                      'HC II'             : 'hcii',
                      'Hospital'          : 'hospital',
                      'HOSPITAL'          : 'hospital',
                    }

def find_facility_type(text):
  rc = re.compile('|'.join(map(re.escape, FACILITY_TYPE_MAP.keys())), re.IGNORECASE)
  result = re.findall(rc, text)
  return FACILITY_TYPE_MAP[result[-1]]


@celery.task
def run_fred_sync():
  fetcher = FredFacilitiesFetcher(FredConfig.get_fred_configs())
  fetcher.sync(current_task.request.id)

@celery.task
def process_facility(facility):
  uuid = facility['id']
  name = facility['name']
  HealthFacilityIdMap.store(uuid, facility['url'])
  existing_facility = HealthFacilityBase.objects.filter(uuid=uuid)
  if existing_facility:
    existing_facility = existing_facility[0]
    existing_facility.name = name.strip()
    existing_facility.save()