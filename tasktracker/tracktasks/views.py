from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from django.utils import timezone
from django.views import generic

from .models import Task



class IndexView(generic.ListView):
    template_name = 'tracktasks/index.html'
    context_object_name = 'daily_tasks_list'

    def get_queryset(self):
        """
        Return all tasks, will later return daily tasks.
        """
        return Task.is_scheduled_for(timezone.now())

def index(request):
    return HttpResponse("Hello, world.")


    # look into the default list view for this and modify to fit needs.


def addtask(request):
    return HTTPResponse("Hello world?")
