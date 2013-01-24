from django.db import models

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

class HealthFacilityIdMap(models.Model):
    uid = models.CharField(primary_key=True,max_length=50,blank=False, null=False)
    url = models.URLField(verify_exists=False)

