from django.urls import path
from .views import user_login, user_logout, register
from . import views

urlpatterns = [
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', register, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('get_users/', views.get_users, name='get_users'),
    path('auth/google/', views.google_auth_callback, name='google_auth_callback'),
    path('auth/google/url/', views.get_google_auth_url, name='google_auth_url'),
    path('auth/google/role/', views.select_role, name='select_role'),
    # path('redirect/', role_based_redirect, name='redirect-after-login'),
]
