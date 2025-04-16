from django.urls import path
from .views import user_login, user_logout, register
from . import views

urlpatterns = [
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', register, name='register'),
    path('get_users/', views.get_users, name='get_users'),
    # path('redirect/', role_based_redirect, name='redirect-after-login'),
]
