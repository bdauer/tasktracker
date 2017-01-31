from tracktasks.models import Task
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from tasktracker.celery import app
from celery.schedules import crontab



@app.task
def daily_updates():
    Task.objects.create_daily_recurring_tasks()
