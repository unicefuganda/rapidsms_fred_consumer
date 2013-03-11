from django.shortcuts import render, redirect
from fred_consumer.models import *
from django.contrib import messages
from django.core.urlresolvers import reverse
from fred_consumer.tasks import run_fred_sync
from celery.task.control import revoke
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def fred_config_page(request):
  settings = FredConfig.get_fred_configs()
  try:
    settings['last_job'] = JobStatus.objects.latest('id')
  except Exception, e:
    settings['last_job'] = None
  return render(request, 'fred_consumer/index.html', settings)

def sync_now(request):
  run_fred_sync.delay()
  messages.success(request, "Sync has been scheduled! Refresh in few seconds.")
  return redirect(reverse('fred_config_page'))

def terminate_job(request):
  last_job = JobStatus.objects.latest('id')
  revoke(last_job.job_id, terminate=True)
  last_job.succeeded(False)
  messages.success(request, "Sync terminated!")
  return redirect(reverse('fred_config_page'))

def failures(request):
  failures = Failure.objects.extra(order_by=["-time"]).all()
  paginator = Paginator(failures, 10)
  page = request.GET.get('page')
  page = int(page) if page else 1

  try:
    failures = paginator.page(page)
  except PageNotAnInteger:
    failures = paginator.page(1)
  except EmptyPage:
    failures = paginator.page(paginator.num_pages)

  return render(request, 'fred_consumer/failures.html', {"failures": failures})