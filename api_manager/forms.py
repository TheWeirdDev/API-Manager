from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import DatabaseInfo, QueryMethod
from django.forms.widgets import Textarea


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(
        max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(
        max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'password1', 'password2', )


class DatabaseForm(forms.ModelForm):
    def __init__(self, is_edit, *args, **kwargs):
        super(DatabaseForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if isinstance(visible.field.widget, Textarea):
                if not is_edit:
                    visible.field.required = False
                visible.field.widget.attrs['class'] = 'textarea'
                visible.field.widget.attrs['rows'] = '5'
            else:
                visible.field.widget.attrs['class'] = 'input'

    class Meta:
        model = DatabaseInfo
        exclude = ('creator', 'changed_date',
                   'created_date', 'running_pid', 'health')


class MethodForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MethodForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if isinstance(visible.field.widget, Textarea):
                visible.field.widget.attrs['class'] = 'textarea'
                visible.field.widget.attrs['rows'] = '5'
            else:
                visible.field.widget.attrs['class'] = 'input'

    class Meta:
        model = QueryMethod
        fields = ('name', 'query_text')
