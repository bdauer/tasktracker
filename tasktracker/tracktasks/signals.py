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

    # only run if the user hasn't logged in for a week.
    # these are users whose tasks aren't regularly updating to save space.
    if user.profile.most_recent_login <\
    datetime.date.today() - datetime.timedelta(days=7):

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

# @receiver(post_init)
# def add_recurring_instance(sender, instance, args, **kwargs):
#     """
#     Create the next instance of a task upon its creation.
#     """
#     # this should only be triggered when a new task is created using the
#     # CreateTaskForm
#     # may need custom signal
