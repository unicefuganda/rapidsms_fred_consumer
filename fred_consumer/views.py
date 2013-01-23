from django.shortcuts import render
from mtrack_project.rapidsms_fred_consumer.fred_consumer.models import *

def fred_config_page(request):
  keys = [FredConfig.URL_KEY, FredConfig.USERNAME_KEY, FredConfig.PASSWORD_KEY]
  settings = {}
  for key in keys:
    result = FredConfig.objects.filter(key=key)
    value = result[0].value if result else ""
    settings[key.lower()] = value
  return render(request, 'fred_consumer/index.html', settings)