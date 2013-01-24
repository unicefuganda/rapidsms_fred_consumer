from django.test import TestCase
from fred_consumer.tasks import run_fred_sync

class TestCeleryTasks(TestCase):

  def test_run_fred_sync(self):
    result = run_fred_sync()
    assert result == True