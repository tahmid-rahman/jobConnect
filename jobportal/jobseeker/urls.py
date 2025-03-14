from django.urls import path, include
from .views import dashboard, company_view, job_detail, setting, profile, tips, insight,company_detail,resume_tips,tips2,tips3,update_profile
from .views import update_about_me,add_work_experience,update_work_experience,delete_work_experience,add_education,update_education,delete_education
from .views import update_job_preferences,add_skills,update_account,change_password,upload_profile_picture,remove_skill,resume_build,apply_job
app_name = 'jobseeker'

from jobseeker.views import dashboard
urlpatterns = [
    path('jobs/', dashboard, name='dashboard'),
    path('jobs/<int:job_id>/', job_detail, name='job_detail'),
    path('company/', company_view, name='company_view'),
    path('company/<int:company_id>/', company_detail, name='company_detail'),
    path('settings/', setting, name='setting'),
    path('profile/', profile, name='profile'),
    path('update_profile/', update_profile, name='update_profile'),
    path('update-about-me/', update_about_me, name='update_about_me'),
    path('add-work-experience/', add_work_experience, name='add_work_experience'),
    path('update-work-experience/<int:id>/', update_work_experience, name='update_work_experience'),
    path('delete-work-experience/<int:id>/', delete_work_experience, name='delete_work_experience'),
    path('add-education/', add_education, name='add_education'),
    path('update-education/<int:id>/', update_education, name='update_education'),
    path('delete-education/<int:id>/', delete_education, name='delete_education'),
    path('update-job-preferences/', update_job_preferences, name='update_job_preferences'),
    path('add-skills/', add_skills, name='add_skills'),
    path('update-account/', update_account, name='update_account'),
    path('change-password/', change_password, name='change_password'),
    path('tips/', tips, name='tips'),
    path('resume-view/<int:id>', resume_build, name='resume_build'),
    path('tips/resume_tips', resume_tips, name='resume_tips'),
    path('tips/interview_tips', tips2, name='tips2'),
    path('tips/networking_tips', tips3, name='tips3'),
    path('salaryinsight/', insight, name='insight'),
    path('apply-job/<int:id>/', apply_job, name='apply_job'),
    path('upload-profile-picture/', upload_profile_picture, name='upload_profile_picture'),
    path('remove-skill/<int:skill_id>/', remove_skill, name='remove_skill'),
]