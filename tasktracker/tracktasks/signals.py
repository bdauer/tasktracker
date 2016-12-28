from django.utils import timezone
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
    tasks_to_repeat = queryset_to_repeat.values()

    # go over the lists, creating new recurring tasks,
    # one recurrence beyond today
    for task in tasks_to_repeat:

        if task.date <= timezone.now():
            next_task = task.add_next_recurring_date()
            tasks_to_repeat.append(next_task)




    # for every task created
    # if the date of the task is before or on today,
    # add_next_recurring_date of the task
    # and add that task to the list.

    # if the date of the task is after today, don't do anything.
