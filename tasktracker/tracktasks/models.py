import datetime
import calendar
import uuid
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import HttpRequest


class TaskManager(models.Manager):
    """
    Override for default Task manager.
    Gets only the current user's tasks by default. Orders tasks by date.

    For specific methods see their respective docstrings.
    """

    def def_queryset(self):
        return super(TaskManager,
        self).get_queryset().order_by('date')

    def scheduled_for(self, request, date, completed=False):
        """
        Return the tasks scheduled for the datetime provided.
        completed: indicates whether to return completed or unfinished tasks.
        """
        if completed:
            return self.filter(
                            date=date,
                            is_completed=True,
                            date_type='S',
                            user=request.user)

        elif not completed:
            return self.filter(
                            date=date,
                            is_completed=False,
                            date_type='S',
                            user=request.user)

    def completed_on(self, request, date_completed):
        """
        Return all tasks completed today.
        """
        return self.filter(
                        completed_date=date_completed,
                        is_completed=True,
                        user=request.user)

    def still_due_on(self, request, duedate):
        """
        Return the non-recurring tasks due after the datetime provided.
        """
        return self.filter(
                        date_type='D',
                        date__gte=duedate,
                        is_completed=False,
                        user=request.user)

    def overdue_on(self, request, duedate):
        """
        Return all past due tasks.
        """
        # datetime issues coming back to haunt me.
        # need to change datetime field to date field and deal with the fallout
        return self.filter(
                        date__lt=duedate,
                        is_completed=False,
                        user=request.user).order_by('-date')


    # This should also be moved to the Manager because
    # it acts on the whole table.
    def create_daily_recurring_tasks():
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

        queryset_to_repeat = Task.objects.filter(date__exact=date_to_check,
                            user__profile__most_recent_login__gte=\
                            active_user_date,
                            is_most_recent=True).exclude(recurring="N")

        for task in queryset_to_repeat:
            task.add_next_recurring_date()




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
    # for tracking related recurring tasks
    recurring_id = models.UUIDField('recurring id', default=uuid.uuid4)
    # for recurring tasks.
    is_most_recent = models.BooleanField(default=False)

    def __str__(self):
        return self.name


    def set_recurring_id(self):
        self.recurring_id = self.id

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
                            'remaining_time', 'recurring_id']

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

            # deal with end of year issues.
            if old_date.month == 12:
                new_month = 1
                new_year = old_date.year + 1
            else:
                new_month = old_date.month + 1
                new_year = old_date.year

            oldcal = calendar.monthdatescalendar(old_date.year,
                                                 old_date.month)
            newcal = calendar.monthdatescalendar(new_year,
                                                 new_month)
            # get the original week and day numbers
            for week in oldcal:
                if old_date in week:
                    week_num = oldcal.index(week)
                    day_num = week.index(old_date)

            new_date = _get_new_date(new_month, newcal, week_num, day_num)

        return new_date

        def _get_new_date(new_month, newcal, week_num, day_num):
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
            # the error can happen
            # when the number of weeks differs
            # between the old and new month.
            except IndexError:
                week_num -= 1
                new_date = newcal[week_num][day_num]

            # Because the monthdatescalendar
            # includes a week from the preceding and following month:
            # ensure we're looking at the correct month.
            if new_date.month < new_month:
                new_date = newcal[week_num + 1][day_num]

            elif new_date.month > new_month:
                new_date = newcal[week_num - 1][day_num]

            return new_date
