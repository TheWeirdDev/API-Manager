from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView
from django.shortcuts import get_object_or_404

from .forms import SignUpForm, ImportDatabaseForm, AddMethodForm
from .models import DatabaseInfo


class HomePage(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        else:
            return redirect('login')


class Dashboard(TemplateView):
    template_name = "dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super(Dashboard, self).dispatch(request, *args, **kwargs)


class DatabaseImport(FormView):
    template_name = "import_db.html"
    form_class = ImportDatabaseForm
    success_url = '/'

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            database = form.save(commit=False)
            database.creator = self.request.user
            database.save()
            return super(DatabaseImport, self).form_valid(form)
        return super(DatabaseImport, self).form_invalid(form)


class AddMethod(FormView):
    template_name = "add_method.html"
    form_class = AddMethodForm
    success_url = '/'

    def get_initial(self):
        initial = super().get_initial()
        self.database = get_object_or_404(
            DatabaseInfo, pk=self.kwargs['database_id'])
        initial['database'] = self.database
        return initial

    def get_success_url(self):
        return reverse('database', kwargs={'database_id': self.database.pk})

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            method = form.save(commit=False)
            method.creator = self.request.user
            method.parent_db = self.database
            method.save()
            return super(AddMethod, self).form_valid(form)
        return super(AddMethod, self).form_invalid(form)


class DatabaseView(TemplateView):
    template_name = "view_db.html"

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
