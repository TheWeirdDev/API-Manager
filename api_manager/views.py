from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView
from django.shortcuts import get_object_or_404
from django.utils import timezone, dateformat
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import auth_login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Q
from django.db.models.functions import Length

import csv
import json

from .forms import SignUpForm, DatabaseForm, MethodForm, SearchForm, TemplateForm
from .models import DatabaseInfo, QueryMethod, CommandTemplate
from .utils import *

LOGIN_URL = '/login/'


class HomePage(View):
    def dispatch(self, request, *args, **kwargs):
        # Home page is the same as dashboard for a logged in user
        # If the user isn't logged in, redirect it to the login page
        if request.user.is_authenticated:
            return redirect('dashboard')
        else:
            return redirect('login')


class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"
    login_url = LOGIN_URL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dbs'] = DatabaseInfo.objects.filter(creator=self.request.user)
        context['methods_count'] = QueryMethod.objects.filter(
            creator=self.request.user).count()
        context['my_dbs'] = True
        return context


class AllApis(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"
    login_url = LOGIN_URL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dbs'] = DatabaseInfo.objects.all()
        context['methods_count'] = QueryMethod.objects.all().count()
        context['my_dbs'] = False
        return context


class DatabaseEdit(LoginRequiredMixin, FormView):
    template_name = "edit_db.html"
    form_class = DatabaseForm
    login_url = LOGIN_URL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        templates = CommandTemplate.objects.all()
        context["templates"] = templates
        t_list = []
        for t in templates:
            t_list.append(
                {'template_id': t.pk, 'name': t.name, 'template_text': t.template_text})
        context["template_list"] = json.dumps(t_list)
        return context

    def get_success_url(self):
        # if 'database_id' is present, then we are in editing mode,
        # otherwise we are in 'add database' page
        if 'database_id' in self.kwargs:
            return reverse('database', kwargs={'database_id': self.database.pk})
        return reverse('dashboard')

    def get_form(self):
        # Form class is populated with data if we are editing a database
        if 'database_id' in self.kwargs:
            self.database = get_object_or_404(
                DatabaseInfo, pk=self.kwargs.get('database_id'))
            return self.form_class(instance=self.database, **self.get_form_kwargs())
        return self.form_class(**self.get_form_kwargs())

    def form_valid(self, form):
        database = form.save(commit=False)

        # If database doesn't have 'creator' property, it has just been created
        if not hasattr(database, 'creator'):
            database.creator = self.request.user

        database.save()
        return super(DatabaseEdit, self).form_valid(form)


class MethodEdit(LoginRequiredMixin, FormView):
    template_name = "edit_method.html"
    form_class = MethodForm
    login_url = LOGIN_URL

    def get_initial(self):
        initial = super().get_initial()
        # Save the parent database of this method so we can redirect to it
        self.database = get_object_or_404(
            DatabaseInfo, pk=self.kwargs['database_id'])
        initial['database'] = self.database
        return initial

    def get_form(self):
        # if 'method_id' is present, then we are in editing mode,
        # and need to populate the form with method name and query
        if 'method_id' in self.kwargs:
            self.method = get_object_or_404(
                QueryMethod, pk=self.kwargs.get('method_id'))
            return self.form_class(instance=self.method, **self.get_form_kwargs())
        return self.form_class(**self.get_form_kwargs())

    def get_success_url(self):
        return reverse('database', kwargs={'database_id': self.database.pk})

    def form_valid(self, form):
        method = form.save(commit=False)
        # If QueryMethod doesn't have 'creator' property, it has just been created
        if not hasattr(method, 'creator'):
            method.creator = self.request.user
            method.parent_db = self.database

        # Save the method, only if it's name is uniqe in the same database
        try:
            method.save()
        except IntegrityError:
            form.add_error(
                'name', "Database already has a method with this name")
            return super(MethodEdit, self).form_invalid(form)
        return super(MethodEdit, self).form_valid(form)


class DatabaseView(LoginRequiredMixin, TemplateView):
    template_name = "view_db.html"
    login_url = LOGIN_URL

    def post(self, request, **kwargs):
        self.database = get_object_or_404(
            DatabaseInfo, pk=self.kwargs['database_id'])
        items = self.database.querymethod_set.all()
        if request.POST.get('print_results', None):
            return print_results(request, items, 'methods')
        if request.POST.get('download_csv', None):
            return download_report(request, items, True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.database = get_object_or_404(
            DatabaseInfo, pk=self.kwargs['database_id'])
        context['database'] = self.database
        return context


@login_required(login_url=LOGIN_URL)
def delete_database(request, database_id):
    """
    Delete a database by providing the database id
    """
    db = get_object_or_404(DatabaseInfo, pk=database_id)
    db.delete()
    return redirect('dashboard')


@login_required(login_url=LOGIN_URL)
def delete_method(request, database_id, method_id):
    """
    Delete a query method by specifying the method id
    """
    method = get_object_or_404(QueryMethod, pk=method_id)
    method.delete()
    return redirect(reverse('database', kwargs={'database_id': database_id}))


@login_required(login_url=LOGIN_URL)
def delete_command_template(request, template_id):
    """
    Delete a template by specifying the template id
    """
    method = get_object_or_404(CommandTemplate, pk=template_id)
    method.delete()
    return redirect(reverse('settings'))


@login_required(login_url=LOGIN_URL)
def search_view(request):
    """
    Search through database by specifying the category and search query
    """
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            is_method = False
            # Get query and category from the form
            query = form.cleaned_data.get('search_query')
            category = form.cleaned_data.get("category")
            # If category is method name, then search methods and render a table for them
            # Otherwise render a table for databases
            if category == "method_name":
                items = QueryMethod.objects.filter(name__contains=query)
                is_method = True
            else:
                # filter by category
                items = DatabaseInfo.objects.filter(
                    **{f'{category}__contains': query}
                )
            return render(request, 'search.html', {'form': form, 'items': items, 'is_method': is_method})
    else:
        form = SearchForm()
        return render(request, 'search.html', {'form': form, 'is_get': True})


def print_results(request, items, category):
    return render(request, 'print.html', {'items': items, 'category': category})


def download_report(request, items, is_methods):
    date_now = dateformat.format(timezone.now(), 'Y-m-d_H-i-s')
    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition':
                f'attachment; filename="report_{date_now}.csv"'},
    )
    writer = csv.writer(response)
    if is_methods:
        write_method_csv(writer, items)
    else:
        write_db_csv(writer, items)
    return response


@login_required(login_url=LOGIN_URL)
def stats_view(request):
    """
    Show total APIs and methods. Allow the user to print or download the results
    """

    all_dbs = DatabaseInfo.objects.all()

    def get_data_for_category(category):
        """
        Helper function for getting different categories from the database
        """
        if category == "all_methods":
            items = QueryMethod.objects.all()
        elif category == "all_dbs":
            items = all_dbs
        return items

    if request.method == 'POST':
        # download_csv is only present if 'Download report' button was clicked
        download_csv_category = request.POST.get('download_csv', None)
        if download_csv_category:
            items = get_data_for_category(download_csv_category)
            is_method = download_csv_category == 'all_methods'
            return download_report(request, items, is_method)

        # Similarly, print_category is present when 'Print' was clicked
        print_category = request.POST.get('print_results', None)
        if print_category:
            items = get_data_for_category(print_category)
            return print_results(request, items, print_category)

        # If those buttons were not clicked, just show the results
        category = request.POST['category']
        is_method = category == 'all_methods'
        items = get_data_for_category(category)
        return render(request, 'stats.html', {'items': items, 'is_method': is_method,
                                              'selected_category': category, })
    else:
        return render(request, 'stats.html', {'items': all_dbs, 'is_method': False,
                                              'selected_category': 'all_dbs'})


def signup(request):
    """
    The signup view renders the signup page and then processes the form
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.save()
            raw_password = form.cleaned_data.get('password1')
            # Login automatically after signup
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'registration/signup.html', {'form': form})
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required(login_url=LOGIN_URL)
def generate_json_config(request, database_id):
    """
    Generates a config file for a database and lets the user download the file
    """
    db = DatabaseInfo.objects.get(pk=database_id)
    config = generate_json(db)
    response = HttpResponse(
        content_type='text/json',
        # Make the config gile downloadable
        headers={
            'Content-Disposition': f'attachment; filename="{db.config_file_name}"',
            'Content-Length': len(config)
        },
    )
    response.write(config)
    return response


class Settings(LoginRequiredMixin, TemplateView):
    template_name = "settings.html"
    login_url = LOGIN_URL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        templates = CommandTemplate.objects.all()
        context['templates'] = templates
        return context


class TemplateEdit(LoginRequiredMixin, FormView):
    template_name = "edit_templates.html"
    form_class = TemplateForm
    login_url = LOGIN_URL

    def get_form(self):
        # if 'template_id' is present, then we are in editing mode
        if 'template_id' in self.kwargs:
            self.template = get_object_or_404(
                CommandTemplate, pk=self.kwargs.get('template_id'))
            return self.form_class(instance=self.template, **self.get_form_kwargs())
        return self.form_class(**self.get_form_kwargs())

    def get_success_url(self):
        return reverse('settings')

    def form_valid(self, form):
        template = form.save(commit=False)

        if not hasattr(template, 'creator'):
            template.creator = self.request.user

        template.save()
        return super(TemplateEdit, self).form_valid(form)
