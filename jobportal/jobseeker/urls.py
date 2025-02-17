from django.urls import path, include
from .views import dashboard, company_view, job_detail, setting, profile, tips, insight,company_detail,resume_tips,tips2,tips3
app_name = 'jobseeker'

from jobseeker.views import dashboard
urlpatterns = [
    path('jobs/', dashboard, name='dashboard'),
    path('jobs/<int:job_id>/', job_detail, name='job_detail'),
    path('company/', company_view, name='company_view'),
    path('company/<int:company_id>/', company_detail, name='company_detail'),
    path('settings/', setting, name='setting'),
    path('profile/', profile, name='profile'),
    path('tips/', tips, name='tips'),
    path('tips/resume_tips', resume_tips, name='resume_tips'),
    path('tips/interview_tips', tips2, name='tips2'),
    path('tips/networking_tips', tips3, name='tips3'),
    path('salaryinsight/', insight, name='insight'),
]