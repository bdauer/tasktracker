import datetime

from django.db import models
from django.db.models import Q
from django.utils import timezone


class Task(models.Model):
    """
    Represents a to-do task.
    Fields:
    name: the name of the task.
    completed_val: the value for completing a task.
    not_completed_cost: the cost of failing to complete a task. (positive num)
    pririty: the importance of a task.
    scheduled_datetime: a date on which the task must be completed.
    due_datetime: a date by which a task must be completed.
    remaining_time: the amount of time required to spend on a task.
    anchor_date: used for calculating recurrence. See inline comment.
    recurring: how frequently a task recurs.
    """
    name = models.CharField(max_length=200)
    priority = models.DecimalField(default=0, max_digits=2, decimal_places=0)

    # Values are used for calculating a score.
    completed_val = models.IntegerField('completed value', default=0)
    not_completed_cost = models.IntegerField('not completed value', default=0)

    # Optional fields. Should include either scheduled or due.
    scheduled_datetime =\
        models.DateTimeField('scheduled date', null=True, blank=True)
    due_datetime =\
        models.DateTimeField('due date', null=True, blank=True)
    remaining_time =\
        models.DurationField('remaining time', null=True, blank=True)

    # The recurring day depends on the anchor date. e.g. weekly recurring
    # happens on the same day of the week. Monthly recurring happens
    # on the same day of the week, of the closest week of the month (probably).
    anchor_date = models.DateField('anchor date', auto_now_add=True)
    FREQUENCY = (('N', 'not recurring'),
                 ('D', 'daily'),
                 ('W', 'weekly'),
                 ('M', 'monthly'),
                )
    recurring = models.CharField(max_length=1,
                                 choices=FREQUENCY,
                                 default='N')

    def __str__(self):
        return self.name

    def is_scheduled_for(datetime):
        """
        Return the tasks scheduled for the datetime provided.
        """
        return Task.objects.filter(
            scheduled_datetime__date=datetime).order_by('scheduled_datetime')

    def is_still_due(before=None):
        """
        Return the tasks due after today.
        Before is a timedelta, returns only within that range from today.
        """
        if not before:
            return Task.objects.filter(
                due_datetime__isnull=False).order_by('due_datetime')

        before_date = datetime.timezone.now() + before
        return Task.objects.filter(
            Q(due_datetime__isnull=False) & Q(due_datetime__lte=before_date))\
                .order_by('due_datetime')
