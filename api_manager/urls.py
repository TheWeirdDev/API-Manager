from django.urls import path
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path('', views.HomePage.as_view(), name='home'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('dashboard/import_db/', views.DatabaseEdit.as_view(), name='import_db'),
    path('dashboard/db/<int:database_id>/edit/',
         views.DatabaseEdit.as_view(), name='edit_db'),
    path('dashboard/db/<int:database_id>/config/',
         views.generate_json_config, name='gen_config'),
    path('dashboard/db/<int:database_id>/',
         views.DatabaseView.as_view(), name='database'),
    path('dashboard/db/<int:database_id>/add_method/',
         views.MethodEdit.as_view(), name='add_method'),
    path('dashboard/db/<int:database_id>/edit_method/<int:method_id>/',
         views.MethodEdit.as_view(), name='edit_method'),
]
