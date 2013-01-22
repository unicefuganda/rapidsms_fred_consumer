from django.shortcuts import render

def fred_config_page(request):
  return render(request, 'fred_consumer/index.html')