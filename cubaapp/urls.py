from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_view, name='indexlogin'),
    # path('loginview', views.login, name='login'),
    path('logout_view', views.logout_view, name='logout_view'),
    path('employee_view', views.viewEmployee, name='employee_view'),
    path('add_employee', views.addEmployee, name='add_employee'),
    path('submit_form/', views.submit_form, name='submit_form'),
    # path('raise_support', views.raise_support,name='raise_support'),
    # path('Documentation', views.Documentation,name='Documentation'),
]