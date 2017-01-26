from tracktasks.models import Task
from django_celery_beat.models import PeriodicTask, CrontabSchedule

schedule, _ = CrontabSchedule.objects.get_or_create(
    minute='*',
    hour='24',
    day_of_week='*',
    day_of_month='*',
    month_of_year='*',
)

PeriodicTask.objects.create(
    crontab=schedule,
    name='recurring updates',
    task='tracktasks.tasks.recurring_updates',
    )
@app.tasks(bind=True)
def recurring_updates():
    Task.objects.create_daily_recurring_tasks()
