from celery import Celery

celery = Celery()

@celery.task
def run_fred_sync():
  return True