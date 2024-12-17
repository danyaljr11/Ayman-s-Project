# urls.py
from django.contrib import admin
from django.urls import path
from app import views


urlpatterns = [
    path('admin/', admin.site.urls),

    # API Endpoints
    path('api/register/', views.RegisterView.as_view(), name='register'),
    path('api/login/', views.LoginView.as_view(), name='login'),
    path('api/logout/', views.LogoutView.as_view(), name='logout'),
    path('api/requests/create/', views.CreateRequestView.as_view(), name='create_request'),
    path('api/requests/list/', views.ListRequestsView.as_view(), name='list_requests'),
    path('api/employees/', views.EmployeeListView.as_view(), name='list_employees'),
    path('api/requests/guest/', views.get_guest_requests, name='get_guest_requests'),
    path('api/requests/employee/', views.get_employee_requests, name='get_employee_requests'),
    path('api/requests/<int:pk>/edit/', views.edit_request, name='edit_request'),

    # Templates Views
    path('', views.render_index, name='index'),
    path('register/', views.render_register, name='register_template'),
    path('login/', views.render_login, name='login_template'),
    path('guest/home/', views.render_guest_home, name='guest_home'),
    path('employee/home/', views.render_employee_home, name='employee_home'),
    path('requests/add/', views.render_add_request, name='add_request'),
    path('requests/edit/<int:pk>/', views.render_edit_request, name='edit_request_template'),
]



