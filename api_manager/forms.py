from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import DatabaseInfo, QueryMethod


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


class ImportDatabaseForm(forms.ModelForm):
    class Meta:
        model = DatabaseInfo
        fields = ('name_en', 'name_fa', 'server_ip', 'server_name',
                  'port_number', 'db_username', 'db_password', 'config_file_name', 'shell_command')


class AddMethodForm(forms.ModelForm):
    class Meta:
        model = QueryMethod
        fields = ('name', 'query_text')
