from django.db import models


class FredConfig(models.Model):
  url       = models.URLField(max_length=200)
  username  = models.CharField(max_length=100)
  password  = models.CharField(max_length=100)


class HealthFacilityIdMap(models.Model):
    uid = models.CharField(primary_key=True,max_length=50,blank=False, null=False)
    url = models.URLField(verify_exists=False)

