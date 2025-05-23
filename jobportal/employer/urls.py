from django.urls import path
from .views import company_dashboard,company_jobs,company_candidates,company_profile,company_settings,company_messages, interview_selection,select_for_interview,interview_complete
from .views import view_job,create_job,delete_job,edit_job,schedule_interview,schedule_delete,take_interview,interview_details,interview_evaluation,view_resume,resume_review,save_marks,save_feedback
from . import views
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
    # path('messages-employer/', company_messages, name='company_messages'),
    path('schedule/', schedule_interview, name='schedule_interview'),
    path('schedule-delete/<int:id>/', schedule_delete, name='schedule_delete'),
    path('interview/<int:id>/', take_interview, name='take_interview'),
    path('interview/<int:id>/save-marks/', save_marks, name='save_marks'),
    path('interview/<int:id>/save-feedback/', save_feedback, name='save_feedback'),
    path('interview-details/<int:id>/', interview_details, name='interview_details'),
    path('interview-evaluation/', interview_evaluation, name='interview_evaluation'),
    path('interview-selection/<int:id>/', interview_selection, name='interview_selection'),
    path('select-for-interview/<int:candidate_id>/', select_for_interview, name='select_for_interview'),
    path('view-resume/<int:resume_id>/', view_resume, name='view_resume'),
    path('view-resume/<int:resume_id>/rate/', resume_review, name='resume_review'),
    path('interview-complete/<int:application_id>/', interview_complete, name='interview_complete'),
    # path('messages/', views.thread_list, name='messages'),
    # path('messages/<int:thread_id>/', views.get_messages, name='get_messages'),
    # path('send_message/', views.send_message, name='send_message'),

]
