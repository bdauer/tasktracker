import datetime

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

        Task.objects.create(name="scheduled 1/16/2017",
                            user=self.user,
                            date_type = "S",
                            date = datetime.date(2017, 1, 16),
                            is_timed=False)

        Task.objects.create(name="scheduled 12/10/2016",
                            user=self.user,
                            date_type = "S",
                            date = datetime.date(2016, 12, 10),
                            is_timed=False)


        self.scheduled_task = Task.objects.get(name="untimed task scheduled today")
        self.task_on_fixed_date = Task.objects.get(name="scheduled 1/16/2017")
        self.fixed_task_end_of_year = Task.objects.get(name="scheduled 12/10/2016")



    def test_string_representation(self):
        """
        Test that the string representation is the instance's name.
        """
        self.assertEqual(str(self.scheduled_task), "untimed task scheduled today")

    def test_complete_task(self):
        """
        Test that completed tasks are marked completed.
        """
        self.scheduled_task.complete()
        self.assertTrue(self.scheduled_task.is_completed)

    def test_add_next_recurring_date_daily(self):
        """
        Test adding a new daily recurring date.
        """
        self.task_on_fixed_date.recurring = 'D'
        self.task_on_fixed_date.add_next_recurring_date()

        next_day_task = Task.objects.get(name="scheduled 1/16/2017",
                                         date=datetime.date(2017, 1, 17))

        self.assertEqual(next_day_task.name, self.task_on_fixed_date.name)

    def test_add_next_recurring_date_weekly(self):
        """
        Test adding a new daily recurring date.
        """
        self.task_on_fixed_date.recurring = 'W'
        self.task_on_fixed_date.add_next_recurring_date()

        next_day_task = Task.objects.get(name="scheduled 1/16/2017",
                                            date=datetime.date(2017, 1, 23))

        self.assertEqual(next_day_task.name, self.task_on_fixed_date.name)

    def test_add_next_recurring_date_biweekly(self):
        """
        Test adding a new biweekly recurring date.
        """
        self.task_on_fixed_date.recurring = 'B'
        self.task_on_fixed_date.add_next_recurring_date()

        next_day_task = Task.objects.get(name="scheduled 1/16/2017",
                                            date=datetime.date(2017, 1, 30))

        self.assertEqual(next_day_task.name, self.task_on_fixed_date.name)

    def test_add_next_recurring_date_monthly(self):
        """
        Test adding a new monthly recurring date.
        """
        self.task_on_fixed_date.recurring = 'M'
        self.task_on_fixed_date.add_next_recurring_date()

        next_day_task = Task.objects.get(name="scheduled 1/16/2017",
                                            date=datetime.date(2017, 2, 20))

        self.assertEqual(next_day_task.name, self.task_on_fixed_date.name)

    def test_add_next_recurring_date_monthly_new_year(self):
        """
        Test adding a new monthly recurring date that changes years.
        The given date is also a case where
        _correct_week_num_offset is tested.
        """
        self.fixed_task_end_of_year.recurring = 'M'
        self.fixed_task_end_of_year.add_next_recurring_date()

        next_day_task = Task.objects.get(name="scheduled 12/10/2016",
                                            date=datetime.date(2017, 1, 14))

        self.assertEqual(next_day_task.name, self.fixed_task_end_of_year.name)


#views tests
    #  def test_index(self):
    #     # Create an instance of a GET request.
    #     request = self.factory.get('tasktracker/tracktasks/')
    #     request.user = self.user
    #     response = IndexView.as_view()(request)
    #     self.assertEqual(response.status_code, 200)
