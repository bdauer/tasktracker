import datetime
import uuid
from django.test import TestCase, RequestFactory
from .models import Task
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.db import models
from .views import IndexView
from userprofiles.models import Profile


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
        one_day = datetime.timedelta(days=1)

        self.user = User.objects.create(username="ben",
                                    password="secure")

        self.user2 = User.objects.create(username="intruder",
                                         password="fuzzypickles")


        # if you add more recurring tasks, update the number.
        num_recurring = 3
        Task.objects.create(name="recurring yesterday",
                            recurring="D",
                            recurring_id=uuid.uuid4(),
                            user=self.user,
                            date_type="S",
                            date=(timezone.now() - one_day),
                            is_most_recent=True,
                            is_disabled=False,
                            pk=1)

        Task.objects.create(name="recurring today",
                            recurring="D",
                            recurring_id=uuid.uuid4(),
                            user=self.user,
                            date_type="S",
                            date=timezone.now(),
                            is_most_recent=True,
                            is_disabled=False,
                            pk=2)

        Task.objects.create(name="recurring tomorrow",
                            recurring="D",
                            recurring_id=uuid.uuid4(),
                            user=self.user,
                            date_type="S",
                            date=(timezone.now() + one_day),
                            is_most_recent=True,
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

        Task.objects.create(name="disabled tomorrow",
                            recurring="N",
                            user=self.user,
                            date_type="S",
                            date=(timezone.now() + one_day),
                            is_disabled=True,
                            pk=7)

        Task.objects.create(name="not_ben tomorrow",
                            recurring="N",
                            user=self.user2,
                            date_type="S",
                            date=(timezone.now() + one_day),
                            is_disabled=False,
                            pk=8)

        Task.objects.create(name="disabled today",
                            recurring="N",
                            user=self.user,
                            date_type="S",
                            date=timezone.now(),
                            is_disabled=True,
                            pk=9)

        Task.objects.create(name="not_ben today",
                            recurring="N",
                            user=self.user2,
                            date_type="S",
                            date=timezone.now(),
                            is_disabled=False,
                            pk=10)

        Task.objects.create(name="disabled yesterday",
                            recurring="N",
                            user=self.user,
                            date_type="S",
                            date=(timezone.now() - one_day),
                            is_disabled=True,
                            pk=11)

        Task.objects.create(name="not_ben yesterday",
                            recurring="N",
                            user=self.user2,
                            date_type="S",
                            date=(timezone.now() - one_day),
                            is_disabled=False,
                            pk=12)

        Task.objects.create(name="dueby recurring yesterday",
                            recurring="D",
                            recurring_id=uuid.uuid4(),
                            user=self.user,
                            date_type="D",
                            date=(timezone.now() - one_day),
                            is_most_recent=True,
                            is_disabled=False,
                            pk=13)

        Task.objects.create(name="dueby recurring today",
                            recurring="D",
                            recurring_id=uuid.uuid4(),
                            user=self.user,
                            date_type="D",
                            date=timezone.now(),
                            is_most_recent=True,
                            is_disabled=False,
                            pk=14)

        Task.objects.create(name="dueby recurring tomorrow",
                            recurring="D",
                            recurring_id=uuid.uuid4(),
                            user=self.user,
                            date_type="D",
                            date=(timezone.now() + one_day),
                            is_most_recent=True,
                            is_disabled=False,
                            pk=15)

    def test_unique_recurring(self):
        """
        Ensure that unique_recurring only gets
        the most recent incomplete instances
        for each recurring task.
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
        Test that all non-disabled tasks are returned.
        """
        all_active = ["<Task: nonrecurring yesterday>",
                         "<Task: nonrecurring today>",
                         "<Task: nonrecurring tomorrow>",
                         "<Task: recurring yesterday>",
                         "<Task: recurring today>",
                         "<Task: recurring tomorrow>",
                         "<Task: dueby recurring yesterday>",
                         "<Task: dueby recurring today>",
                         "<Task: dueby recurring tomorrow>"]

        self.assertQuerysetEqual(Task.objects.active_tasks(self.user),
                                 all_active, ordered=False)

    def test_scheduled_for(self):
        """
        Test that for a given date, gets all tasks scheduled for that date.
        """

        scheduled_today = ["<Task: nonrecurring today>",
                           "<Task: recurring today>",
                           "<Task: dueby recurring today>"]

        self.assertQuerysetEqual(Task.objects.scheduled_for(self.user,
                                                            timezone.now()),
                                 scheduled_today, ordered=False)

    def test_completed_on(self):
        """
        Ensure that it returns all tasks completed on a given day
        and not tasks given on a different day.
        """
        completed_today = ["<Task: nonrecurring today>"]

        # test against incomplete tasks.
        self.assertQuerysetEqual(Task.objects.completed_on(self.user,
                                                           timezone.now()),
                                 [])

        nonrecurring = Task.objects.get(name="nonrecurring today")
        nonrecurring.is_completed = True
        nonrecurring.completed_date = timezone.now()
        nonrecurring.save()
        # test against complete task.
        self.assertQuerysetEqual(Task.objects.completed_on(self.user,
                                                           timezone.now()),
                                 completed_today)


    def test_still_due_on(self):
        """
        Ensure that it returns tasks that are still due by a given date,
        and not scheduled tasks still due.
        """
        scheduled_today = ["<Task: dueby recurring tomorrow>",
                           "<Task: dueby recurring today>",
                           "<Task: dueby recurring yesterday>"]
        # tests that a new recurring task
        # will properly display
        # if the prior task was completed.
        dueby_yesterday = Task.objects.get(name="dueby recurring yesterday")
        dueby_yesterday.add_next_recurring_date()
        dueby_yesterday.is_completed = True
        dueby_yesterday.save()

        self.assertQuerysetEqual(Task.objects.still_due_on(self.user,
                                                           timezone.now()),
                                 scheduled_today, ordered=False)

    def test_overdue_on(self):
        """
        Ensure that it returns tasks overdue on a given date.
        """
        overdue_today = ["<Task: dueby recurring yesterday>",
                      "<Task: nonrecurring yesterday>",
                      "<Task: recurring yesterday>"]

        overdue_qs = Task.objects.overdue_on(self.user, timezone.now())

        self.assertQuerysetEqual(overdue_qs, overdue_today, ordered=False)




    def test_create_daily_recurring_tasks(self):
        """
        Ensure that for every recurring task, the most recent recurring instance
        is used to make a new instance.
        """
        one_day = datetime.timedelta(days=1)
        new_tasks = ["<Task: recurring yesterday>",
                     "<Task: recurring tomorrow>",
                     "<Task: recurring today>",
                     "<Task: dueby recurring yesterday>",
                     "<Task: dueby recurring tomorrow>",
                     "<Task: dueby recurring today>"]

        Task.objects.create_daily_recurring_tasks()

        # mark old tasks incomplete
        # this will need to change after the incomplete bug is fixed.
        tasks_qs = Task.objects.unique_recurring(self.user)
        for task in tasks_qs:
            task.is_completed = True
            task.completed_date = (timezone.now() - one_day)
            task.save()

        # get the newest tasks after updating completion
        new_tasks_qs = Task.objects.unique_recurring(self.user)

        for task in new_tasks_qs:
            task_group = Task.objects.filter(name__exact=task.name)

            # when a task was impacted by daily recurring tasks,
            # make sure that the new instance exists in new_tasks_qs.
            if len(task_group) == 2:
                self.assertEqual(task_group[1].pk, task.pk)
            # if it wasn't effected,
            # make sure the old task exists in new_tasks_qs.
            if len(task_group) == 1:
                self.assertEqual(task_group[0].pk, task.pk)

    def test_get_task_group_incompletes(self):
        """
        Test that for a given shared_id, it returns all recurrences
        after the provided date.
        """
        recurring_task = Task.objects.get(pk=1)
        recurring_task.add_next_recurring_date()

        # test with no completed tasks
        recurrences = Task.objects.get_task_group_incompletes(
                                                recurring_task.recurring_id)
        self.assertEqual(len(recurrences), 2)

        # test with a completed task
        recurring_task.is_completed = True
        recurring_task.save()
        recurrences = Task.objects.get_task_group_incompletes(
                                                recurring_task.recurring_id)
        self.assertEqual(len(recurrences), 1)

    def test_disable_recurrences(self):
        """
        Test that running disable_recurrences disables all future instances
        of a recurring task.
        """
        recurring_task = Task.objects.get(pk=1)
        recurring_task.add_next_recurring_date()

        Task.objects.disable_recurrences(recurring_task.recurring_id)

        recurrences = Task.objects.filter(
                                    recurring_id=recurring_task.recurring_id)

        self.assertEqual(len(recurrences), 2)
        for recurrence in recurrences:
            self.assertEqual(recurrence.is_disabled, True)




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
