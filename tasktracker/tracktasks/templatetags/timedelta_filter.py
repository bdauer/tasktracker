# adapted from http://stackoverflow.com/a/36058967

from django import template
from datetime import date, timedelta

register = template.Library()

@register.filter(name='format_timedelta')
def format_timedelta(value):
    hours, remainder = divmod(value.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours != 0:
        return '{}h:{}m:{}s'.format(hours, minutes, seconds)
    if (hours == 0) and (minutes == 0):
        return '{}s'.format(seconds)
    if (hours == 0):
        return '{}m:{}s'.format(minutes, seconds)
