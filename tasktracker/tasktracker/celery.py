import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tasktracker.settings')

app=Celery('tasktracker')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace=`CELERY` means all celery-related config keys
# should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(['tracktasks'])

@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    from tracktasks.tasks import recurring_updates
    sender.add_periodic_task(crontab(minute=0, hour=0),
                             daily_updates.s(), name='daily updates')
