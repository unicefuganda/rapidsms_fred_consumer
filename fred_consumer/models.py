from django.db import models
import datetime
import settings

class FredConfig():
  @classmethod
  def get_settings(self):
      return settings.CONNECT_TO_FRED_KEYS

class JobStatus(models.Model):
  PENDING = "PENDING"
  SUCCESS = "SUCCESS"
  FAILED  = "FAILED"

  job_id = models.CharField(max_length=100)
  time   = models.DateTimeField(auto_now_add=True)
  status = models.CharField(max_length=50)

  def succeeded(self, success):
    self.status = self.SUCCESS if success else self.FAILED
    self.save()

class HealthFacilityIdMap(models.Model):
    uuid = models.CharField(primary_key=True, max_length=50)
    url = models.URLField(verify_exists=True)

    @classmethod
    def store(self, uuid, url):
        self.objects.get_or_create(uuid=uuid, url=url)

class Failure(models.Model):
  time      = models.DateTimeField(auto_now_add=True)
  exception = models.TextField()
  json      = models.TextField()
  action = models.TextField(default="GET")