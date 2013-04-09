from urllib2 import HTTPError
from fred_consumer.models import Failure
import json

def capture_urllib_exception(fn):
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except HTTPError, e:
            request = args[1]
            exception = type(e).__name__ +":"+ str(e.read()) + ":" + request.get_full_url()
            json = request.data if request.data else ""
            Failure.objects.create(exception=exception, json=json, action = request.get_method())
            raise e
    return wrapped

def capture_generic_exception(fn):
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except HTTPError, e:
            raise e
        except Exception, e:
            if len(args) > 2:
                facility = args[2]
                facility['uuid'] = args[1]
            else:
                facility = args[1]
            exception = type(e).__name__ +":"+ str(e)
            Failure.objects.create(exception=exception, json=json.dumps(facility), action = "GENERIC")
            raise e
    return wrapped

def return_in_boolean(fn):
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception, e:
            return False
    return wrapped