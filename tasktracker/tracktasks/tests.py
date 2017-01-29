import datetime
import uuid
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

class TaskManagerTestCases(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="ben",
                                    password="secure")

        self.user2 = User.objects.create(username="intruder",
                                         password="fuzzypickles")

        one_day = datetime.timedelta(days=1)
        # if you add more recurring tasks, update the number.
        num_recurring = 3
        Task.objects.create(name="recurring yesterday",
                            recurring="D",
                            recurring_id=uuid.uuid4(),
                            user=self.user,
                            date_type="S",
                            date=(timezone.now() - one_day),
                            is_disabled=False,
                            pk=1)

        Task.objects.create(name="recurring today",
                            recurring="D",
                            recurring_id=uuid.uuid4(),
                            user=self.user,
                            date_type="S",
                            date=timezone.now(),
                            is_disabled=False,
                            pk=2)

        Task.objects.create(name="recurring tomorrow",
                            recurring="D",
                            recurring_id=uuid.uuid4(),
                            user=self.user,
                            date_type="S",
                            date=(timezone.now() + one_day),
                            is_disabled=False,
                            pk=3)

        Task.objects.create(name="nonrecurring yesterday",
                            recurring="N",
                            user=self.user,
                            date_type="S",
                            date=(timezone.now() - one_day),
                            is_disabled=False,
                            pk=4)

        Task.objects.create(name="nonrecurring today",
                            recurring="N",
                            user=self.user,
                            date_type="S",
                            date=timezone.now(),
                            is_disabled=False,
                            pk=5)

        Task.objects.create(name="nonrecurring tomorrow",
                            recurring="N",
                            user=self.user,
                            date_type="S",
                            date=(timezone.now() + one_day),
                            is_disabled=False,
                            pk=6)

    def test_unique_recurring(self):
        """
        Ensure that unique_recurring only gets
        the most recent incomplete instances
        for each recurring task.

        Need to create recurring tasks for today, earlier, later.

        Should create a separate test that runs the same check
        after some tasks have been completed.
        """
        recurring_tasks = Task.objects.exclude(recurring="N")

        recurring_ids = set()

        for task in recurring_tasks:
            recurring_ids.add(task.recurring_id)
            task.add_next_recurring_date()

        for recurring_id in recurring_ids:
            recurring_group = Task.objects.filter(recurring_id=recurring_id)


            recur_list = Task.objects.unique_recurring(self.user)

            # check against the original recurrence.
            if recurring_group[0] in recur_list:
                continue
            else:
                self.fail(recurring_group[0])

            self.assertEqual(len(recur_list), num_recurring)
        pass

    def test_unique_recurring_completed(self):
        """
        Same as before,
        but check against tasks marked as completed and ensure they don't show.
        """
        recurring_tasks = Task.objects.exclude(recurring="N")

        recurring_ids = set()

        for task in recurring_tasks:
            recurring_ids.add(task.recurring_id)
            task.add_next_recurring_date()
            task.is_completed = True
            task.save()

        for recurring_id in recurring_ids:
            recurring_group = Task.objects.filter(recurring_id=recurring_id)
            recur_list = Task.objects.unique_recurring(self.user)

            # check against the newer recurrence.
            if recurring_group[1] in recur_list:
                continue
            else:
                self.fail(recurring_group[0])

            self.assertEqual(len(recur_list), num_recurring)
        pass

    def test_non_recurring(self):
        """
        Ensure that this gets all of the non-recurring, incomplete tasks.
        """
        one_day = datetime.timedelta(days=1)
        non_recurring = ["<Task: nonrecurring yesterday>",
                         "<Task: nonrecurring today>",
                         "<Task: nonrecurring tomorrow>"]

        self.assertQuerysetEqual(Task.objects.non_recurring(self.user),
                                 non_recurring)

    def test_active_tasks(self):
        """
        test that all non-disabled tasks are returned.
        """
        pass

    def test_scheduled_for(self):
        """
        Test that for a given date, gets all tasks scheduled for that date.

        need tasks scheduled for different dates.
        """
        pass

    def test_completed_on(self):
        """
        Ensure that it returns all tasks completed on a given day

        and not tasks given on a different day.
        """
        pass

    def test_still_due_on(self):
        """
        Ensure that it returns tasks that are still due for a given date,
        and not scheduled tasks still due.

        Need future scheduled and due tasks.
        """
        pass

    def test_overdue_on(self):
        """
        Ensure that it returns tasks overdue on a given date,
        including scheduled tasks.
        """
        pass


    def test_create_daily_recurring_tasks(self):
        """
        Ensure that for every recurring task, the most recent recurring instance
        is used to make a new instance.

        Will need several different recurring tasks.
        """
        pass

    def test_get_future_recurrences(self):
        """
        Test that for a given shared_id, it returns all recurrences
        after the provided date.

        Should also run after marking a recurring task as complete.
        """
        pass

    def test_disable_recurrences(self):
        """
        Test that running disable_recurrences disables all future instances
        of a recurring task.
        """
        pass




# for the TaskManager methods, build data to check different cases.
# should include three of every category that could get pulled.
# they can overlap.
# if you have new tests in the future, don't add new setup data.
# either stick with what you've got, or create a new TestCase class

#views tests
    #  def test_index(self):
    #     # Create an instance of a GET request.
    #     request = self.factory.get('tasktracker/tracktasks/')
    #     request.user = self.user
    #     response = IndexView.as_view()(request)
    #     self.assertEqual(response.status_code, 200)
