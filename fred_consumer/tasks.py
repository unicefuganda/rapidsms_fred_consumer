from celery import Celery, current_task
from fred_consumer.models import JobStatus

celery = Celery()

@celery.task
def run_fred_sync():
  JobStatus.objects.create(job_id=current_task.request.id, status=JobStatus.PENDING)
  return True