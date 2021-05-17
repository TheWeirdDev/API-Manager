from django.urls import path
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path('', views.HomePage.as_view(), name='home'),
    path('signup/', views.signup, name='signup'),
    path('dashboard', views.Dashboard.as_view(), name='dashboard'),
    path('dashboard/import_db/', views.DatabaseImport.as_view(), name='import_db'),
    path('dashboard/db/<int:database_id>',
         views.DatabaseView.as_view(), name='database'),
    path('dashboard/db/<int:database_id>/add_method',
         views.AddMethod.as_view(), name='add_method'),
]
