#!/usr/bin/env python

import urllib2
import json
import base64
from fred_consumer.models import HealthFacilityIdMap

JSON_EXTENSION = ".json"

class FredFacilitiesFetcher(object):

    # connection_setting : contains the user/password for the server
    def __init__(self,connection_setting):
        auth = base64.b64encode("%(user)s:%(password)s" % connection_setting)
        self.HEADERS = {
            'Content-type': 'application/json; charset="UTF-8"',
            'Authorization': 'Basic '+auth
        }

    # url is appended with .json by default
    def get(self, url, extension=JSON_EXTENSION,paging=True):
        url += extension + '?paging=' + str(paging).lower()
        req = urllib2.Request(url, headers=self.HEADERS)
        response = urllib2.urlopen(req)
        return json.loads(response.read())

    def get_facility(self, url, facility_id, extension=JSON_EXTENSION):
        extension = "/" + str(facility_id)  + extension
        return self.get(url,extension)

    def get_filtered_facilities(self,url, filters, extension=JSON_EXTENSION):
        url += extension
        for key, value in filters.items():
            url += '?' + str(key) + "=" + str(value)
        return self.get(url,"", paging=False)

class ReadFacility(object):
    def __init__(self,facility):
        self.facility = facility

    def create_facility_map(self):
        HealthFacilityIdMap(uid=self.facility['id'], url=self.facility['url']).save()

    def process_facility(self):
        if not self.does_facility_exists():
            self.create_facility_map()
        return self.facility

    def does_facility_exists(self):
        return bool(HealthFacilityIdMap.objects.filter(uid=self.facility['id']))