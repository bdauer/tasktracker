from django import forms
from .models import Task
import datetime


class ModifyTaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ['name', 'date_type', 'date', 'is_timed',
                  'total_time', 'recurring','is_disabled']
        widgets = {
                'date':  forms.SelectDateWidget(),
                'total_time': forms.TimeInput(attrs={'placeholder':'hh:mm:ss'}),
        }
        help_texts = {
    }
        labels = {
            'is_disabled': 'Delete task',
        }



class CreateTaskForm(forms.ModelForm):



    class Meta:
        model = Task
        fields = ['name', 'date_type', 'date',
                  'is_timed', 'total_time', 'recurring']
        widgets = {
                'date':  forms.SelectDateWidget(),
                'total_time': forms.TimeInput(attrs={'placeholder':'hh:mm:ss'}),
        }
        help_texts = {
        }
