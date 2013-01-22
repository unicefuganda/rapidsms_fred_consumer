from django.shortcuts import render
from mtrack_project.rapidsms_fred_consumer.fred_consumer.models import *

def fred_config_page(request):
  settings = FredConfig.objects.all()
  if len(settings) == 0:
    settings = FredConfig()
  else:
    settings = settings[0]
  return render(request, 'fred_consumer/index.html', {'settings': settings})