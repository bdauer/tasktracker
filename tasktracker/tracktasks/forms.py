from django import forms
from .models import Task

class CreateTaskForm(forms.ModelForm):


    # def __init__(self, *args, **kwargs):
    #     self.user = kwargs.pop('user')
    #     super(CreateTaskForm, self).__init__(*args, **kwargs)
    #
    # def save(self, user, commit=True):
    #     task = forms.ModelForm.save(self, commit=False)
    #     task.user = user
    #     if commit:
    #         task.save()
    #     return task

    class Meta:
        model = Task
        fields = ['name', 'date_type', 'date',
                  'is_timed', 'total_time', 'recurring']
        widgets = {
                'date':  forms.SelectDateWidget(),
                'total_time': forms.TimeInput(),
        }
        help_texts = {
            'total_time': ('minutes.'),
        }
