from django.db import models

class FredConfig(models.Model):
  URL_KEY = 'URL'
  USERNAME_KEY = 'USERNAME'
  PASSWORD_KEY = 'PASSWORD'
  key       = models.CharField(max_length=255, unique=True)
  value     = models.CharField(max_length=255)

class HealthFacilityIdMap(models.Model):
    uid = models.CharField(primary_key=True,max_length=50,blank=False, null=False)
    url = models.URLField(verify_exists=False)

