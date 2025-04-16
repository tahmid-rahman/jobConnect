from django.urls import path
from .views import  admin_home 
app_name = 'adminpanel'

urlpatterns = [
    path('', admin_home, name='admin_home'),
]