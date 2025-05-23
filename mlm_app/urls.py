from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication URLs
    path('', views.home, name='home'),
    path('auth/login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('auth/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('auth/register/', views.register, name='register'),
    
    # Dashboard URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/profile/', views.profile, name='profile'),
    path('dashboard/genealogy/', views.genealogy, name='genealogy'),
    path('dashboard/income-report/', views.income_report, name='income_report'),
    path('dashboard/select-plan/', views.select_plan, name='select_plan'),
    
    # Service URLs
    path('services/mobile-recharge/', views.initiate_recharge, name='mobile_recharge'),
    
    # Admin URLs
    path('admin-panel/plans/', views.admin_plans, name='admin_plans'),
    path('admin-panel/members/', views.admin_members, name='admin_members'),
    
    # API URLs
    path('api/member-search/', views.api_member_search, name='api_member_search'),
]
