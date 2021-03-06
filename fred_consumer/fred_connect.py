#!/usr/bin/env python
import urllib
import urllib2
import json
import base64
from fred_consumer.models import HealthFacilityIdMap, JobStatus, FredConfig
from fred_consumer.decorators import *
from django.core.exceptions import ObjectDoesNotExist
import re

JSON_EXTENSION = ".json"

class FredFacilitiesFetcher(object):

    def __init__(self,connection_setting):
        auth = base64.b64encode("%(username)s:%(password)s" % connection_setting)
        self.BASE_URL = connection_setting['url'].strip("/")
        self.FACILITY_URL_PREFIX = self.BASE_URL + "/facilities"
        self.DHIS_ORG_UNIT_URL = connection_setting["dhis_org_unit_url"]
        self.HEADERS = {
            'Content-type': 'application/json; charset="UTF-8"',
            'Authorization': 'Basic '+auth
        }

    @capture_urllib_exception
    def send(self, request):
        return urllib2.urlopen(request)

    def get(self, extension, url = None, query = None):
        url = (url or self.BASE_URL) + extension
        if query:
            url += "?" + query
        request = urllib2.Request(url, headers=self.HEADERS)
        return self.send(request)

    def get_json(self, extension, url = None, query = None, etag = False):
        response = self.get(extension, url, query)
        facility_json = json.loads(response.read())
        etag_header = response.info().getheader('ETag')
        return [facility_json, etag_header] if etag else facility_json

    def write(self, facility_url, facility_data, action="POST", headers={}):
        headers.update(self.HEADERS)
        request = urllib2.Request(facility_url + JSON_EXTENSION, data = json.dumps(facility_data), headers = headers)
        request.get_method = lambda: action
        return self.send(request)

    def get_all_facilities(self):
        return self.get_json(url = self.FACILITY_URL_PREFIX, extension = JSON_EXTENSION, query = "limit=off")

    def get_facility(self, facility_id, etag = False):
        url = HealthFacilityIdMap.objects.get(uuid=facility_id).url
        return self.get_json(url = url, extension= JSON_EXTENSION, etag = etag)

    def get_filtered_facilities(self, filters):
        query = []
        for key, value in filters.items():
            query.append(key + "=" + value)
        query = "&".join(query)
        return self.get_json(url = self.FACILITY_URL_PREFIX, query = query, extension = JSON_EXTENSION)

    def fetch_facilities(self):
      try:
        job_status = JobStatus.objects.filter(status=JobStatus.SUCCESS).latest('time')
        facilities = self.get_filtered_facilities({'updatedSince': job_status.time.strftime("%Y-%m-%dT%H:%M:%SZ")})
      except ObjectDoesNotExist:
        facilities = self.get_all_facilities()
      return facilities

    def sync(self, job_id):
        from fred_consumer.tasks import process_facility
        status = JobStatus.objects.create(job_id=job_id, status=JobStatus.PENDING)
        try:
            facilities = self.fetch_facilities()
            for facility in facilities['facilities']:
                process_facility.delay(facility)
            status.succeeded(True)
        except Exception:
            status.succeeded(False)

    def get_district(self, url):
      location = self.get_json(url = url, extension = JSON_EXTENSION)
      if 'district' in location['name'].lower():
          return location['name']
      else:
        return self.get_district(location['parent']['href'])


    def get_locations_for_facility(self, parent_id):
        location_hash = {}
        parent_facility_url = self.DHIS_ORG_UNIT_URL + parent_id
        parent_facility = self.get_json(url = parent_facility_url, extension = JSON_EXTENSION)
        location_hash["subcounty"] = re.sub('Subcounty.*$|Sub\ County.*$', "", parent_facility["name"]).strip()
        district = parent_facility['name'] if 'district' in parent_facility['name'].lower() else self.get_district(parent_facility['parent']['href'])
        location_hash["district"] = re.sub('District.*$', "", district).strip()
        return location_hash

    @capture_generic_exception
    def update_facilities_in_provider(self, facility_id, facility):
        facility_in_fred, etag = self.get_facility(facility_id, etag = True)
        facility = dict(facility_in_fred.items() + facility.items())
        facility_url = HealthFacilityIdMap.objects.get(uuid=facility_id).url
        headers = {}
        if etag:
            headers["If-Match"] = etag
        self.write(facility_url, facility, "PUT", headers)
        return True

    @capture_generic_exception
    def create_facility_in_provider(self, facility):
        response = self.write(self.FACILITY_URL_PREFIX, facility)
        facility_url = response.info().getheader('Location')
        facility_in_fred = self.get_json(url = facility_url, extension= JSON_EXTENSION)
        facility_id = facility_in_fred['uuid']
        HealthFacilityIdMap.store(facility_id, facility_url)
        return facility_id

    @staticmethod
    @return_in_boolean
    def send_facility_update(health_facility):
        fetcher = FredFacilitiesFetcher(FredConfig.get_settings())
        facility = {'name': health_facility.name, 'active': health_facility.active}
        return fetcher.update_facilities_in_provider(health_facility.uuid, facility)

    @staticmethod
    @return_in_boolean
    def create_facility(health_facility):
        fetcher = FredFacilitiesFetcher(FredConfig.get_settings())
        facility = {'name': health_facility.name,
                    'active': True,
                    'coordinates': [0,0]
                    }
        return fetcher.create_facility_in_provider(facility)
