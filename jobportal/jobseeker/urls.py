from django.urls import path, include
from .views import dashboard
app_name = 'jobseeker'

from jobseeker.views import dashboard
urlpatterns = [
    path('', dashboard, name='dashboard'),
]