import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.views import generic
from django.urls import reverse
from django.core.urlresolvers import reverse_lazy
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from .forms import CreateTaskForm


from userprofiles.models import Profile

from .models import Task

import logging

logger = logging.getLogger(__name__)

class IndexView(LoginRequiredMixin, generic.ListView):
    """
    Shows all of today's tasks.
    """

    template_name = 'tracktasks/index.html'
    model = Task

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['daily_tasks_list'] = Task.objects.scheduled_for(self.request, datetime.date.today())
        data['still_due_tasks_list'] = Task.objects.still_due_on(self.request,
                                                         datetime.date.today())
        data['completed_tasks_list'] = Task.objects.completed_on(self.request,
                                                        datetime.date.today())
        data['overdue_tasks_list'] = Task.objects.overdue_on(self.request,
                                                     datetime.date.today())
        return data

class ManageTasksView(LoginRequiredMixin, generic.ListView):
    """
    Show all of a user's tasks.
    """
    template_name = 'tracktasks/managetasks.html'
    model = Task
    context_object_name = 'user_tasks'

    def get_queryset(self):
        return Task.objects.filter(is_completed=False)

@login_required
def mark_task_complete(request):
    """
    Mark a task complete, start a timer or stop a timer.
    Probably will move the latter two out later.
    """


    if (request.method == 'POST' or request.is_ajax()) and 'selected_task' in request.POST:
        task_id = request.POST['selected_task']
        # if 'name' in request.POST:
        print(request.POST)
        name = request.POST['name']
        task = Task.objects.get(pk=task_id)

        if "completed" in name:
            task.complete()

        elif "start_timer" in name:
            task.start_time = timezone.now()

        elif "stop_timer" in name:
            try:
                elapsed_time = timezone.now() - task.start_time
            except TypeError:
                task.start_time = timezone.now()
                elapsed_time = timezone.now() - task.start_time
            task.remaining_time -= elapsed_time
            task.start_time = None

            # only the days attribute of a timedelta
            # will go negative.
            if task.remaining_time.days < 0:
                print("less than or equal to zero")
                task.complete()

        task.save()

    return HttpResponse()


class CreateTaskView(LoginRequiredMixin, generic.CreateView):
    """
    Create a new task.
    """
    form_class = CreateTaskForm
    template_name = 'tracktasks/createtask.html'

    def get_success_url(self):
        return reverse_lazy('tracktasks:index')

    def form_valid(self, form):
        form.instance.user = self.request.user

        if form.instance.is_timed:
            # convert from seconds to minutes
            form.instance.total_time *=60
            form.instance.remaining_time = form.instance.total_time

        # add next recurrence for recurring tasks.
        if form.instance.recurring != 'N':
            first_task = form.save(commit=False)
            Task.add_next_recurring_date(first_task)

        return super(CreateTaskView, self).form_valid(form)
