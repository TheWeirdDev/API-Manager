from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import SignUpForm, DatabaseForm, MethodForm
from .models import DatabaseInfo, QueryMethod

from .utils import run_command, check_status, stop_docker
import json
import time

LOGIN_URL = '/login/'


class HomePage(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        else:
            return redirect('login')


class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"
    login_url = LOGIN_URL


class DatabaseEdit(LoginRequiredMixin, FormView):
    template_name = "edit_db.html"
    form_class = DatabaseForm
    login_url = LOGIN_URL

    def get_success_url(self):
        if 'database_id' in self.kwargs:
            return reverse('database', kwargs={'database_id': self.database.pk})
        return reverse('dashboard')

    def get_form(self):
        if 'database_id' in self.kwargs:
            self.database = get_object_or_404(
                DatabaseInfo, pk=self.kwargs.get('database_id'))
            return self.form_class(True, instance=self.database, **self.get_form_kwargs())
        return self.form_class(False, **self.get_form_kwargs())

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            database = form.save(commit=False)
            if not hasattr(database, 'creator'):
                database.creator = self.request.user
            else:
                database.changed_date = timezone.now()
            database.save()
            return super(DatabaseEdit, self).form_valid(form)
        return super(DatabaseEdit, self).form_invalid(form)


class MethodEdit(LoginRequiredMixin, FormView):
    template_name = "edit_method.html"
    form_class = MethodForm
    login_url = LOGIN_URL

    def get_initial(self):
        initial = super().get_initial()
        self.database = get_object_or_404(
            DatabaseInfo, pk=self.kwargs['database_id'])
        initial['database'] = self.database
        return initial

    def get_form(self):
        if 'method_id' in self.kwargs:
            self.database = get_object_or_404(
                QueryMethod, pk=self.kwargs.get('method_id'))
            return self.form_class(instance=self.database, **self.get_form_kwargs())
        return self.form_class(**self.get_form_kwargs())

    def get_success_url(self):
        return reverse('database', kwargs={'database_id': self.database.pk})

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            method = form.save(commit=False)
            if not hasattr(method, 'creator'):
                method.creator = self.request.user
                method.parent_db = self.database
            else:
                method.changed_date = timezone.now()
            method.save()
            return super(MethodEdit, self).form_valid(form)
        return super(MethodEdit, self).form_invalid(form)


class DatabaseView(LoginRequiredMixin, TemplateView):
    template_name = "view_db.html"
    login_url = LOGIN_URL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.database = get_object_or_404(
            DatabaseInfo, pk=self.kwargs['database_id'])
        context['database'] = self.database
        return context


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Load the profile instance that was created by the signal
            user.refresh_from_db()
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required(login_url=LOGIN_URL)
def generate_json_config(request, database_id):
    db = DatabaseInfo.objects.get(pk=database_id)
    methods_dict = {i.name: i.query_text for i in db.querymethod_set.all()}
    methods = [{name: query} for name, query in methods_dict.items()]
    config = {
        'server': db.server_ip,
        'database': db.name_en,
        'user': db.db_username,
        'password': db.db_password,
        'methods': methods
    }
    data = json.dumps(config)
    response = HttpResponse(
        content_type='text/json',
        headers={
            'Content-Disposition': f'attachment; filename="{db.config_file_name}"',
            'Content-Length': len(data)
        },
    )
    response.write(data)
    return response


@login_required(login_url=LOGIN_URL)
def run_api(request, database_id):
    database = get_object_or_404(DatabaseInfo, pk=database_id)
    if database.docker_id != "":
        return JsonResponse({'error': "API is already running"})
    docker_id = run_command(database.shell_command)
    resp = {'running': False, 'docker_id': docker_id, 'health_ok': False}
    if docker_id != "" and docker_id != None:
        database.docker_id = docker_id
        database.save()
        resp['running'] = True
        time.sleep(0.5)
        if check_status(database) == 200:
            resp['health_ok'] = True
            database.health = True
            database.save()
    return JsonResponse(resp)


@login_required(login_url=LOGIN_URL)
def stop_api(request, database_id):
    database = get_object_or_404(DatabaseInfo, pk=database_id)
    if database.docker_id == "":
        return JsonResponse({'error': "API is not running"})
    if stop_docker(database.docker_id):
        database.docker_id = ""
        database.health = False
        database.save()
        return JsonResponse({'running': "False"})
    else:
        return JsonResponse({'error': "Can't stop API"})


@login_required(login_url=LOGIN_URL)
def check_health(request, database_id):
    database = get_object_or_404(DatabaseInfo, pk=database_id)
    if database.docker_id == "":
        return JsonResponse({'error': 'API is not running'})
    if check_status(database) == 200:
        database.health = True
        database.save()
        return JsonResponse({'health_ok': True})
    else:
        database.health = False
        database.save()
        return JsonResponse({'error': 'API status code is not 200'})
