from django.db import models

class FredConfig(models.Model):
  url       = models.URLField(max_length=200)
  username  = models.CharField(max_length=100)
  password  = models.CharField(max_length=100)