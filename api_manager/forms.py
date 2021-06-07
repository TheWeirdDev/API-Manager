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


class SearchForm(forms.Form):
    categories = (('name_en', "Project Name (EN)"),
                  ('name_fa', 'Project Name (FA)'),
                  ('db_name', 'Database Name'),
                  ('method_name', 'Method Name '),
                  ('server_name', 'Server Name '),
                  ('server_ip', 'Server IP'),
                  ('config_file_name', 'Config File Name'),
                  )
    category = forms.ChoiceField(
        label='Category', widget=forms.Select, choices=categories)
    search_query = forms.CharField(
        max_length=100, widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Search...'}))


class DatabaseForm(forms.ModelForm):
    def __init__(self, is_edit, *args, **kwargs):
        super(DatabaseForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            # Find the shell command widget
            if isinstance(visible.field.widget, Textarea):
                # Only require shell command if user is editing the database
                if not is_edit:
                    visible.field.required = False
                # Shell command is a textarea and so should have this css class
                visible.field.widget.attrs['class'] = 'textarea'
                visible.field.widget.attrs['rows'] = '5'
            else:
                # Other fields are input widgets and will have 'input' css class
                visible.field.widget.attrs['class'] = 'input'

    class Meta:
        model = DatabaseInfo
        # These fields are not going to be provided by the user
        exclude = ('creator', 'changed_date',
                   'created_date', 'docker_id', 'health')


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
