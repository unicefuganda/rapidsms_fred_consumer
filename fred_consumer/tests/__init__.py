from django.core import management

def setup():
  management.call_command('loaddata', 'locations', verbosity=0)

def teardown(self):
  management.call_command('flush', verbosity=0, interactive=False)

