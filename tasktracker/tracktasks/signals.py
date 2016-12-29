from django.utils import timezone
import datetime
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from tracktasks.models import Task


@receiver(user_logged_in)
def update_recurring_tasks(sender, request, user, **kwargs):
    """
    Create recurring tasks for user from their last login through one
    beyond today.
    """

    # get all tasks from last login until today where the user is the
    # current user and recurring is not none.
    queryset_to_repeat = Task.objects.filter(date__lte=timezone.now(),
                        date__gt=user.profile.most_recent_login,
                        user=user).exclude(recurring="N")

    list_to_repeat = []

    # go over the lists, creating new recurring tasks,
    # one recurrence beyond today
    for task in queryset_to_repeat:

        if task.date <= datetime.date.today():
            next_task = task.add_next_recurring_date()
            list_to_repeat.append(next_task)

    for task in list_to_repeat:

        if task.date <= datetime.date.today():
            next_task = task.add_next_recurring_date()
            list_to_repeat.append()

    # def _repeat_and_append(task, list_to_repeat):
    #     """
    #     Return the list_to_repeat list.
    #
    #     Check if the task's date is less than or equal to today.
    #     If it is, create a new task.
    #     Append the new task to the list_to_repeat list.
    #     """
    #
    #     if task.date <= timezone.now():
    #         next_task = task.add_next_recurring_date()
    #         list_to_repeat.append(next_task)
    #         return (list_to_repeat)




    # for every task created
    # if the date of the task is before or on today,
    # add_next_recurring_date of the task
    # and add that task to the list.

    # if the date of the task is after today, don't do anything.
