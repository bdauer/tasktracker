import datetime
import calendar
import uuid
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.core.exceptions import ObjectDoesNotExist


class TaskManager(models.Manager):
    """
    Override for default Task manager.
    For specific methods see their respective docstrings.
    """
    def get_queryset(self):
        return super(TaskManager,
        self).get_queryset().order_by('date')

    def unique_recurring(self, user, multiple=False):
        """
        Return a queryset containing
        the most recent incomplete instances
        of each group of active recurring tasks
        for the provided user.
        """
        unique_ids = self._get_unique_recurring_ids(user)
        latest_recurring_ids = self._get_latest_recurring(unique_ids, multiple)
        latest_recurring = self.filter(pk__in=latest_recurring_ids)
        return latest_recurring

    def _get_unique_recurring_ids(self, user):
        """
        Return a set of unique recurring_ids
        for active recurring tasks.
        """
        unique_ids = set()
        recurrences = self.filter(user=user,
                                is_disabled=False).exclude(recurring='N')
        # construct set of unique recurring ids
        for recurrence in recurrences:
            recurring_id = recurrence.recurring_id
            if recurring_id not in unique_ids:
                unique_ids.add(recurring_id)
        return(unique_ids)

    def _get_latest_recurring(self, unique_ids, multiple=False):
        """
        Return a list of the latest recurring instances.
        If multiple is True, try to return multiple instances of the same task.
        If multiple is False, return only one instance per task.
        """
        latest_recurring = set()

        for recurring_id in list(unique_ids):
            recurring_group = self.filter(recurring_id=recurring_id)

            if multiple:
                candidates = recurring_group.filter(is_completed=False)
                if len(candidates) != 0:
                    for candidate in candidates:
                        latest_recurring.add(candidate.id)
                else:
                    candidate = recurring_group.filter(
                                            is_completed=True).latest('date')
                    latest_recurring.add(candidate.id)

            elif not multiple:
                try:
                    candidate = recurring_group.filter(
                        is_completed=False).earliest('date')
                except ObjectDoesNotExist:
                    candidate = recurring_group.filter(
                        is_completed=True).latest('date')
                latest_recurring.add(candidate.id)
        return latest_recurring

    def non_recurring(self, user):
        """
        Return a queryset containing
        all active, non-recurring, incomplete task instances.
        """
        return self.filter(
                        is_completed=False,
                        user=user,
                        is_disabled=False,
                        recurring='N')

    def active_tasks(self, user, multiple=False):
        """
        Return all active tasks for the provided user.
        """
        recurring_query = self.unique_recurring(user, multiple)
        non_recurring_query = self.non_recurring(user)
        return (recurring_query | non_recurring_query).order_by('date')

    def scheduled_for(self, user, date, completed=False):
        """
        Return the tasks scheduled for the datetime provided.
        completed: indicates whether to return completed or unfinished tasks.
        """
        active_tasks = self.active_tasks(user, multiple=True)
        return active_tasks.filter(date=date)

    def completed_on(self, user, date_completed):
        """
        Return all tasks completed on date_completed.
        """
        return self.filter(
                        completed_date=date_completed,
                        is_completed=True,
                        user=user,
                        is_disabled=False).order_by('date')

    def still_due_on(self, user, duedate):
        """
        Return the non-recurring tasks due after the datetime provided.
        """
        active_tasks = self.active_tasks(user)
        return active_tasks.filter(date_type='D',
                                   date__gte=duedate).order_by('date')

    def overdue_on(self, user, duedate):
        """
        Return all past due tasks.
        """
        active_tasks = self.active_tasks(user, multiple=True)
        return active_tasks.filter(
                        date__lt=duedate,
                        is_completed=False,
                        is_disabled=False,
                        user=user).order_by('-date')

    def create_daily_recurring_tasks(self):
        """
        Create a new recurrence
        for all most recent recurring tasks
        that happen tomorrow.

        This function should be run daily.

        It checks for tomorrow to avoid timezone conflicts
        for those whose time zone is near the update time.
        """
        active_user_date = timezone.now() - datetime.timedelta(days=7)
        date_to_check = datetime.date.today() + datetime.timedelta(days=1)

        queryset_to_repeat = Task.objects.filter(
                            date__exact=date_to_check,
                            user__profile__most_recent_login__gte=\
                            active_user_date,
                            is_most_recent=True,
                            is_disabled=False).exclude(recurring="N")

        for task in queryset_to_repeat:
            task.add_next_recurring_date()
            task.is_most_recent = False


    def get_task_group_incompletes(self, shared_id):
        """
        Get all future recurrences of a recurring task.
        """
        recurrences = Task.objects.filter(
                            recurring_id=shared_id,
                            is_completed=False)
        return recurrences

    def disable_recurrences(self, shared_id):
        """
        Get all future recurrences of a task
        using the provided id
        and set them as disabled.
        """
        recurrences = self.get_task_group_incompletes(shared_id)
        for task in recurrences:
            task.is_disabled = True
            task.save()

# Opted against inheritance for different types of tasks because
# it doesn't translate well into a relational model.
# might consider a one-to-one relationship for dealing with:
# timed and recurring tasks.
class Task(models.Model):
    """
    Represents a to-do task.
    Fields:
    name: the name of the task.
    priority: the importance of a task.
    is_completed: true if the task has been completed.

    completed_val: the value for completing a task.
    not_completed_cost: the cost of failing to complete a task.(positive num)

    date_type: tells whether the task is scheduled on or due by the date field.
    date: the date that a task is either scheduled for or due by.

    start_time: the time at which a task was started.
    remaining_time: the amount of time required to spend on a task.
    anchor_date: used for calculating recurrence. See inline comment.
    recurring: how frequently a task recurs.
    """
    objects = TaskManager()
    user = models.ForeignKey(User, null=True)

    name = models.CharField(max_length=200)
    priority = models.DecimalField(default=0, max_digits=2, decimal_places=0)

    is_completed = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)

    # Values are used for calculating a score.
    completed_val = models.IntegerField('completed value', default=0)
    not_completed_cost = models.IntegerField('not completed value', default=0)

    # Because separate scheduled and due dates were leading to repeated,
    # longer queries I've opted for a date field and a date_type field.
    DATE_TYPES = (('S', 'scheduled for'),
                  ('D', 'due by'),
                 )
    date_type = models.CharField('date type', max_length=1,
                                 choices=DATE_TYPES, default='D')
    date = models.DateField()

    is_timed = models.BooleanField(default=False)
    total_time = models.DurationField('total time', null=True, blank=True)

    # The following fields only apply to timed events.
    # start_time is recorded at the start of a task. When the time is stopped,
    # the total difference is subtracted from remaining_time. When it is
    # restarted, start_time is overwritten.
    # In the future it may be worth saving start/stop times and the task for
    # analysis.
    start_time = models.DateTimeField('start time', null=True, blank=True)
    remaining_time =\
        models.DurationField('remaining time', null=True, blank=True)

    # The recurring day depends on the anchor date. e.g. weekly recurring
    # happens on the same day of the week. Monthly recurring happens
    # on the same day of the week, of the closest week of the month (probably).
    anchor_date = models.DateField('anchor date', auto_now_add=True)
    FREQUENCY = (('N', 'not recurring'),
                 ('D', 'daily'),
                 ('W', 'weekly'),
                 ('B', 'biweekly'),
                 ('M', 'monthly'),
                )
    recurring = models.CharField(max_length=1,
                                 choices=FREQUENCY,
                                 default='N')
    # for tracking related recurring tasks. If not recurring, use NULL_RECURRING
    NULL_RECURRING = '00000000-0000-0000-0000-000000000000'
    recurring_id = models.UUIDField('recurring id', default=NULL_RECURRING)
    # for recurring tasks.
    is_most_recent = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def complete(self):
        """
        Mark a task as complete
        and set its completed date.
        """
        self.is_completed = True
        self.completed_date = timezone.now()

    def add_next_recurring_date(self):
        """
        create and return a new recurrance of a recurring task.
        """
        new_task = Task()
        unchanged_fields = ['name', 'priority', 'completed_val',
                            'not_completed_cost', 'date_type',
                            'is_timed', 'recurring', 'total_time', 'user',
                            'remaining_time', 'recurring_id', 'is_most_recent']

        for field in unchanged_fields:
            old_field_value = getattr(self, field)
            setattr(new_task, field, old_field_value)

        new_task.date = self._assign_recurring_date()
        new_task.save()

        return new_task

    def _assign_recurring_date(self):
        """
        returns the next recurring date.

        In the case of monthly recurring tasks, they happen on the same
        day of the week, of the same week of the month.
        """
        old_date = self.date

        if self.recurring == 'D':
            new_date = old_date + datetime.timedelta(days=1)
        elif self.recurring == 'W':
            new_date = old_date + datetime.timedelta(days=7)
        elif self.recurring == 'B':
            new_date = old_date + datetime.timedelta(days=14)
        elif self.recurring == 'M':

            new_month, new_year = self._check_for_year_change(old_date)

            recur_cal = calendar.Calendar(0)
            oldcal = recur_cal.monthdatescalendar(old_date.year,
                                                    old_date.month)
            newcal = recur_cal.monthdatescalendar(new_year,
                                                 new_month)
            # get the original week and day numbers
            for week in oldcal:
                if old_date in week:
                    week_num = oldcal.index(week)
                    day_num = week.index(old_date)

            new_date = self._get_new_date(new_month, new_year, oldcal,
                                          newcal, week_num, day_num)

        return new_date

    def _get_new_date(self, new_month, new_year, oldcal,
                      newcal, week_num, day_num):
        """
        Return the next recurring date for monthly recurrence.

        Checks that the week isn't out of index.
        Checks that the month is correct.

        params:
        new_month: the numeric value of the new task's month.
        newcal: a monthdatescalendar object for the new month.
        week_num: the original week number.
        day_num: the original number for the day of the week.
        """

        try:
            new_date = newcal[week_num][day_num]
        except IndexError:
            # the error can happen
            # when the number of weeks differs
            # between the old and new month.
            week_num -= 1
            new_date = newcal[week_num][day_num]

        week_num = self._correct_week_num_offset(oldcal, newcal,
                                                 day_num, week_num)

        # Because the monthdatescalendar
        # includes a week from the preceding and following month:
        # ensure we're looking at the correct month.
        if  new_date.month < new_month:
            week_num += 1

        if new_date.month > new_month:
            week_num -= 1

        new_date = newcal[week_num][day_num]
        return new_date

    def _correct_week_num_offset(self, oldcal, newcal, day_num, week_num):
        """
        Return a week_num with an offset
        based on the differences in weekday values
        between two Calendar.monthdatescalendar objects.

        Explanation:
        The monthdatescalendar includes
        a week from the prior month.

        In some cases a weekday
        from the current month
        can occur in that week.

        When this happens in one and only one of the passed monthdatescalendars,
        we need to create an offset to account for the difference.
        """
        old_first_week_day = oldcal[0][day_num]
        old_third_week_day = oldcal[2][day_num]
        new_first_week_day = newcal[0][day_num]
        new_third_week_day = newcal[2][day_num]
        old_offset = (old_first_week_day.month == old_third_week_day.month)
        new_offset = (new_first_week_day.month == new_third_week_day.month)

        if old_offset and not new_offset:
            week_num += 1

        elif new_offset and not old_offset:
            week_num -= 1

        return week_num

    def _check_for_year_change(self, old_date):
        """
        Return the new month and year,
        one month advanced from the old date.
        """
        if old_date.month == 12:
            new_month = 1
            new_year = old_date.year + 1
        else:
            new_month = old_date.month + 1
            new_year = old_date.year

        return new_month, new_year
