import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
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
        data['daily_tasks_list'] = Task.is_scheduled_for(self.request,
                                                         datetime.date.today())
        data['still_due_tasks_list'] = Task.is_still_due(self.request,
                                                         datetime.date.today())
        data['completed_tasks_list'] = Task.was_completed_on(self.request,
                                                        datetime.date.today())
        data['overdue_tasks_list'] = Task.is_overdue(self.request,
                                                     datetime.date.today())
        return data

@login_required
def mark_task_complete(request):
    """
    Mark a task complete, start a timer or stop a timer.
    Probably will move the latter two out later.
    """

    if request.method == 'POST' and 'selected_task' in request.POST:

        task_id = request.POST['selected_task']
        task = Task.objects.get(pk=task_id)

        if "completed" in request.POST:
            task.complete()

        elif "start_timer" in request.POST:
            task.start_time = timezone.now()

        elif "stop_timer" in request.POST:
            elapsed_time = timezone.now() - task.start_time
            task.remaining_time -= elapsed_time

            task.start_time = None

            if task.remaining_time.days < 0:
                task.complete()

        task.save()

    return HttpResponseRedirect(reverse('tracktasks:index'))


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
        form.instance.remaining_time = form.instance.total_time
        return super(CreateTaskView, self).form_valid(form)
