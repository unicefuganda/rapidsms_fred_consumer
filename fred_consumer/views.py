from django.shortcuts import render, redirect
from mtrack_project.rapidsms_fred_consumer.fred_consumer.models import *
from django.contrib import messages
from django.core.urlresolvers import reverse

def fred_config_page(request):
  keys = [FredConfig.URL_KEY, FredConfig.USERNAME_KEY, FredConfig.PASSWORD_KEY]
  settings = {}
  for key in keys:
    result = FredConfig.objects.filter(key=key)
    value = result[0].value if result else ""
    settings[key.lower()] = value
  return render(request, 'fred_consumer/index.html', settings)

def fred_update_config(request):
  keys = [FredConfig.URL_KEY, FredConfig.USERNAME_KEY, FredConfig.PASSWORD_KEY]
  for key in keys:
    config = FredConfig.objects.get_or_create(key=key)[0]
    config.value = request.POST[key.lower()]
    config.save()
  messages.success(request, "Configurations updated successfully!")
  return redirect(reverse('fred_config_page'))