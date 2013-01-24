from django.shortcuts import render, redirect
from fred_consumer.models import *
from django.contrib import messages
from django.core.urlresolvers import reverse

def fred_config_page(request):
  return render(request, 'fred_consumer/index.html', FredConfig.get_fred_configs())

def fred_update_config(request):
  FredConfig.store_fred_configs(request.POST)
  messages.success(request, "Configurations updated successfully!")
  return redirect(reverse('fred_config_page'))