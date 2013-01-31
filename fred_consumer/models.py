from django.db import models
import datetime

class FredConfig(models.Model):
  URL_KEY = 'URL'
  USERNAME_KEY = 'USERNAME'
  PASSWORD_KEY = 'PASSWORD'
  KEYS = [URL_KEY, USERNAME_KEY, PASSWORD_KEY]

  key       = models.CharField(max_length=255, unique=True)
  value     = models.CharField(max_length=255)

  @classmethod
  def get_fred_configs(self):
    settings = {}
    for key in self.KEYS:
      result = self.objects.filter(key=key)
      value = result[0].value if result else ""
      settings[key.lower()] = value
    return settings

  @classmethod
  def store_fred_configs(self, params):
    for key in self.KEYS:
      config = self.objects.get_or_create(key=key)[0]
      config.value = params[key.lower()]
      config.save()

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