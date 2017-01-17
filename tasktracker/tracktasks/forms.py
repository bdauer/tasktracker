from django import forms
from .models import Task
import datetime



def display_field_values(fields, kwargs):
    for field in fields:
        widget = fields[field].widget
        field_type = widget.__class__.__name__
        initial_value = kwargs['initial'][field]

        if any(item in field_type for item in ["TimeInput", "TextInput"]):
            widget.attrs['value'] = initial_value

        elif field_type == "CheckboxInput":
            if fields[field].widget.check_test(initial_value):
                widget.attrs['checked'] = ''
        elif field_type == "Select":
            print(field_type)
            for choice in widget.choices:
                if initial_value in choice:
                    print(choice)
                    print(initial_value)
                    # print(widget.render_option(selected_choices=initial_value, option_value=choice[0], option_label=choice[1]))

        elif field_type == "SelectDateWidget":
            print(widget.data)

class ModifyTaskForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super(ModifyTaskForm, self).__init__(*args, **kwargs)

        display_field_values(self.fields, kwargs)

        # for field in self.fields:
        #     widget = self.fields[field].widget
        #     field_type = widget.__class__.__name__
        #     initial_value = kwargs['initial'][field]
        #
        #     if any(item in field_type for item in ["TimeInput", "TextInput"]):
        #         widget.attrs['value'] = initial_value
        #
        #     elif field_type == "CheckboxInput":
        #         if self.fields[field].widget.check_test(kwargs['initial'][field]):
        #             widget.attrs['checked'] = ''
        #     elif field_type == "Select":
        #         print(field_type)

        #  try messing with this some more.
        # consider how to access the name attrs.
        # check docs for fields to understand how it's set up

    # name = forms.CharField(widget=forms.TextInput(attrs={'value': 'name'}))



    class Meta:
        model = Task
        fields = ['id','name', 'date_type', 'date',
                  'is_timed', 'total_time', 'recurring']
        widgets = {
                'date':  forms.SelectDateWidget(),
                'total_time': forms.TimeInput(),
        }
        help_texts = {
            'total_time': ('minutes.'),
    }



class CreateTaskForm(forms.ModelForm):



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
