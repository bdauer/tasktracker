from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^addtask/$', views.CreateTaskView.as_view(), name='create task'),
    url(r'^marktaskcomplete/$', views.mark_task_complete, name='mark complete')
]
