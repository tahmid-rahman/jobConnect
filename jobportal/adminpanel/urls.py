from django.urls import path
from .views import  admin_home 
from . import views
app_name = 'adminpanel'

urlpatterns = [
    path('', admin_home, name='admin_home'),
    path('user-management/', views.user_management, name='user_management'),
    path('job-postings-management/', views.job_management, name='job_management'),
    path('content-management/', views.content_management, name='content_management'),
    path('feedback-analytics/', views.feedback_analytics, name='feedback_analytics'),
    path('platform-security/', views.platform_security, name='platform_security'),
    path('settings/', views.settings, name='settings'),
    path('settings/site-configuration/', views.site_configuration, name='site_configuration')
]