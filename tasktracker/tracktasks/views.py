from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q

# Create your views here.


def index(request):
    return HttpResponse("Hello, world.")


    # look into the default list view for this and modify to fit needs.


def addtask(request):
    return HTTPResponse("Hello world?")
