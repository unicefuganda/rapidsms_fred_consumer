#!/usr/bin/env python

import httplib2
import base64
import json
import time

Http = httplib2.Http
http = Http()

JSON_EXTENSION = ".json"

#Uses basic HTTP authorization
class Fred_Facilities_Fetcher(object):

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
        response, content = http.request(url, 'GET', headers=self.HEADERS)
        return json.loads(content)

    def get_facility(self, url, facility_id, extension=JSON_EXTENSION):
        extension = "/" + str(facility_id)  + extension
        return self.get(url,extension)

    def get_filtered_facilities(self,url, filters, extension=JSON_EXTENSION):
        url += extension
        for key, value in filters.items():
            url += '?' + str(key) + "=" + str(value)
        return self.get(url,extension, paging=False)


class Update_Facilities(object):

    def __init__(self,facilities_list):
        self.facilities = facilities_list

    def does_facility_exists_in_mtrack(self,facility):
        facility['id']
