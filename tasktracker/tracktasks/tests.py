from django.test import TestCase, RequestFactory
from .models import Task
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.db import models
from .views import IndexView


# Create your tests here.

# models tests
class TaskTestCases(TestCase):

    def setUp(self):
        self.factory = RequestFactory
        self.user = User.objects.create(username="not_ben",
                                    password="secure")

        Task.objects.create(name="untimed task scheduled today",
                            user=self.user,
                            date_type = "S",
                            date = timezone.now(),
                            is_timed=False) # default, but added to be explicit

        self.scheduled_task = Task.objects.get(name="untimed task scheduled today")



    def test_string_representation(self):

        self.assertEqual(str(self.scheduled_task), "untimed task scheduled today")

    def test_complete_task(self):
        self.scheduled_task.complete()
        self.assertTrue(self.scheduled_task.is_completed)



#views tests
    #  def test_index(self):
    #     # Create an instance of a GET request.
    #     request = self.factory.get('tasktracker/tracktasks/')
    #     request.user = self.user
    #     response = IndexView.as_view()(request)
    #     self.assertEqual(response.status_code, 200)
