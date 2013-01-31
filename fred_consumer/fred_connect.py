#!/usr/bin/env python
import urllib2
import json
import base64
from fred_consumer.models import HealthFacilityIdMap, JobStatus
from django.core.exceptions import ObjectDoesNotExist

JSON_EXTENSION = ".json"

class FredFacilitiesFetcher(object):

    def __init__(self,connection_setting):
        auth = base64.b64encode("%(username)s:%(password)s" % connection_setting)
        self.BASE_URL = connection_setting['url'].strip("/")
        self.HEADERS = {
            'Content-type': 'application/json; charset="UTF-8"',
            'Authorization': 'Basic '+auth
        }

    def get(self, extension, query = None):
        url = self.BASE_URL + extension
        if query:
            url += "?" + query
        request = urllib2.Request(url, headers=self.HEADERS)
        response = urllib2.urlopen(request)
        return json.loads(response.read())

    def get_all_facilities(self):
      extension = "/facilities" + JSON_EXTENSION
      return self.get(extension)

    def get_facility(self, facility_id):
        extension = "/facilities/" + str(facility_id)  + JSON_EXTENSION
        return self.get(extension)

    def get_filtered_facilities(self, filters):
        query = []
        for key, value in filters.items():
            query.append(key + "=" + value)
        query = "&".join(query)
        extension = "/facilities.json"
        return self.get(query=query, extension=extension)

    def sync(self):
      from fred_consumer.tasks import process_facility

      try:
        job_status = JobStatus.objects.latest('time')
        facilities = self.get_filtered_facilities({'updatedSince': job_status.time.strftime("%Y-%m-%dT%H:%M:%SZ")})
      except ObjectDoesNotExist:
        facilities = self.get_all_facilities()

      for facility in facilities['facilities']:
        process_facility.delay(facility)
