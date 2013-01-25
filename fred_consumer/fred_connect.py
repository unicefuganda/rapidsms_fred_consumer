#!/usr/bin/env python

import urllib2
import json
import base64
from fred_consumer.models import HealthFacilityIdMap

JSON_EXTENSION = ".json"

class FredFacilitiesFetcher(object):

    def __init__(self,connection_setting):
        auth = base64.b64encode("%(username)s:%(password)s" % connection_setting)
        self.BASE_URL = connection_setting['url'].strip("/")
        self.HEADERS = {
            'Content-type': 'application/json; charset="UTF-8"',
            'Authorization': 'Basic '+auth
        }

    def get(self, extension=JSON_EXTENSION, query = None):
        url = self.BASE_URL + extension
        if query:
            url += "?" + query
        request = urllib2.Request(url, headers=self.HEADERS)
        response = urllib2.urlopen(request)
        return json.loads(response.read())

    def get_facility(self, facility_id):
        extension = "/" + str(facility_id)  + JSON_EXTENSION
        return self.get(extension)

    def get_filtered_facilities(self, filters):
        query = []
        for key, value in filters.items():
            query.append(key + "=" + value)
        query = "&".join(query)
        return self.get(query=query)

#class FredFacilityWriter(object):
#    def __init__(self,connection_setting):
#        auth = base64.b64encode("%(user)s:%(password)s" % connection_setting)
#        HEADERS = {
#            'Content-type': 'application/json; charset="UTF-8"',
#            'Authorization': 'Basic '+auth
#        }
#
#    def write(self, facility_data, action):
#        request = urllib2.Request(facility_data['url'], headers = self.HEADERS)
#        request.add_data(urllib2.urlencode(facility_data))
#        request.get_method = lambda: action
#        return urllib2.urlopen(request)
#
#
#class WriteFacilityToFred(object):
#    def __init__(self,facility):
#        self.facility = facility
#
#    def construct_fred_facility_object(self):
#        facility_in_map_url = HealthFacilityIdMap.objects.filter(uid=self.facility['id'])[0].url
#        facility_in_fred = FredFacilitiesFetcher.get(facility_in_map_url)
#        for field in facility_in_fred:
#            if self.facility.has_key(field):
#                facility_in_fred[field] = self.facility[field]
#        return facility_in_fred
#
#    def put_facility(self):
#        facility_in_fred = self.construct_fred_facility_object()
#
#        FredFacilityWriter.write(facility_in_fred, "put")
#
#
#
#
#
#
