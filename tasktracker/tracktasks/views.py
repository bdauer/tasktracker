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
    context_object_name = 'daily_tasks_list'

    def get_queryset(self):
        """
        Return all tasks, will later return daily tasks.
        """
        return Task.is_scheduled_for(timezone.now()).filter(is_completed=False)

        # next step is to filter by completed tasks.



def mark_task_complete(request):

    if request.method == 'POST' and 'selected_task' in request.POST:

        task_id = request.POST['selected_task']

        task = Task.objects.get(pk=task_id)
        task.is_completed = True
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
        return HttpResponse(task.is_completed)

# def index(request):
#     return HttpResponse("Hello, world.")


    # look into the default list view for this and modify to fit needs.


def addtask(request):
    return HttpResponse("Hello world?")
