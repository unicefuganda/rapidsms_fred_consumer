from django.core import management

def setup():
  # management.call_command('loaddata', 'locations', verbosity=0)
  from rapidsms.contrib.locations.models import Location
  Location.objects.create(name="Uganda")

def teardown(self):
  management.call_command('flush', verbosity=0, interactive=False)

