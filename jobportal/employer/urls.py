from django.urls import path
from .views import company_dashboard,company_jobs,company_candidates,company_profile,company_settings,company_messages
from .views import view_job,create_job,delete_job,edit_job,schedule_interview,schedule_delete,take_interview,interview_details

app_name = 'employer'

urlpatterns = [
    path('', company_dashboard, name='company_dashboard'),
    path('jobs/', company_jobs, name='company_jobs'),
    path('jobs/view/<int:job_id>/', view_job, name='view_job'),
    path('create_job/', create_job, name='create_job'),
    path('jobs/edit/<int:job_id>/', edit_job, name='edit_job'),
    path('jobs/delete/<int:job_id>/', delete_job, name='delete_job'),
    path('candidates/', company_candidates, name='company_candidates'),
    path('profile/', company_profile, name='company_profile'),
    path('settings/', company_settings, name='company_settings'),
    path('messages/', company_messages, name='company_messages'),
    path('schedule/', schedule_interview, name='schedule_interview'),
    path('schedule-delete/<int:id>/', schedule_delete, name='schedule_delete'),
    path('interview/<int:id>/', take_interview, name='take_interview'),
    path('interview-details/<int:id>/', interview_details, name='interview_details'),
]
