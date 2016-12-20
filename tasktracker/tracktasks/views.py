import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.db.models import Q
from django.utils import timezone
from django.views import generic
from django.urls import reverse



from .models import Task

import logging

logger = logging.getLogger(__name__)



class IndexView(generic.ListView):
    template_name = 'tracktasks/index.html'
    model = Task
    # context_object_name = 'daily_tasks_list'


    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['daily_tasks_list'] = Task.is_scheduled_for(timezone.now())
        data['still_due_tasks_list'] = Task.is_still_due(timezone.now())
        data['completed_tasks_list'] = Task.is_scheduled_for(timezone.now(),\
                                                             completed=True)
        data['overdue_tasks_list'] = Task.is_overdue(timezone.now())
        return data


def mark_task_complete(request):

    if request.method == 'POST' and 'selected_task' in request.POST:

        task_id = request.POST['selected_task']
        task = Task.objects.get(pk=task_id)

        if "completed" in request.POST:
            task.is_completed = True

        elif "start_timer" in request.POST:
            task.start_time = timezone.now()

        elif "stop_timer" in request.POST:
            elapsed_time = timezone.now() - task.start_time
            task.remaining_time -= elapsed_time

            if task.remaining_time.days < 0:
                task.is_completed = True

            task.start_time = None

        task.save()

    # logger.info("hello")
    # task_id = request.object.task.id
    #
    # completed_task = get_object_or_404(Task, id=task_id)
    #
    # form = DeleteTaskForm(request.POST, instance=completed_task)
    #
    # if form.is_valid():
    #     completed_task.is_completed = True
    #     completed_task.save()
    #     return HttpResponseRedirect('/tracktasks/')
    # else:
    #     form = DeleteTaskForm(instance=new_to_delete)
    #
    # template_vars = {'form': form}
    # return render(request, 'tracktasks/index.html', template_vars)
    return HttpResponse(task.remaining_time.days)

# def index(request):
#     return HttpResponse("Hello, world.")


    # look into the default list view for this and modify to fit needs.


def addtask(request):
    return HttpResponse("Hello world?")
