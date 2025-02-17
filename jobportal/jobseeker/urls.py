from django.urls import path, include
from .views import dashboard, company_view, job_detail, setting, profile, tips, insight
app_name = 'jobseeker'

from jobseeker.views import dashboard
urlpatterns = [
    path('jobs/', dashboard, name='dashboard'),
    path('jobs/<int:job_id>/', job_detail, name='job_detail'),
    path('company/', company_view, name='company_view'),
    path('settings/', setting, name='setting'),
    path('profile/', profile, name='profile'),
    path('tips/', tips, name='tips'),
    path('salaryinsight/', insight, name='insight'),
]