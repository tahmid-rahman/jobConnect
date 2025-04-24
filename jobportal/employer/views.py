import json
from datetime import datetime, timedelta
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Count,Subquery,Prefetch,F, ExpressionWrapper, FloatField
from employer.models import Job,Company, JobApplication,Interview
from jobseeker.models import Profile,Skill,Contact,JobPreference
from accounts.models import CustomUser as User
# from adminpanel.models import Message, MessageThread





def employee_role_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'employee':
            messages.error(request, "You are not authorized to view this page.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@employee_role_required
@login_required
def company_dashboard(request):
    comp  = Company.objects.get(user=request.user)
    active_jobs_count = Job.objects.filter(company__user=request.user, status="Active").count()
    applications = JobApplication.objects.filter(job__company__user=request.user, job__status="Active").count()
    scheduled = Interview.objects.filter(application__job__company__user=request.user).count()

    return render(request, 'employee/employee_home.html', {
                'active_jobs_count': active_jobs_count, 
                'applications': applications, 
                'scheduled': scheduled,
                'company':comp
                }) 


@employee_role_required
@login_required
def company_jobs(request):
    # jobs_list = Job.objects.filter(company__user=request.user).order_by('-posted_date')  
    jobs_list = Job.objects.filter(company__user=request.user).annotate(applicant_count=Count('jobapplication')).order_by('-posted_date')
    paginator = Paginator(jobs_list, 9)
    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number) 

    return render(request, 'employee/emp_jobs.html', {'page_obj': page_obj})


@employee_role_required
@login_required
def company_candidates(request):
    applicant = JobApplication.objects.filter(
        job__company__user=request.user, job__status="Active"
    ).select_related('applicant', 'job').prefetch_related(
        Prefetch('applicant__skills', queryset=Skill.objects.all())
    ).order_by('-applied_date')
    return render(request, 'employee/candidate.html',{'candidate':applicant}) 

# @employee_role_required
# @login_required
# def company_profile(request):
#     profile = get_object_or_404(Profile, user= request.user)
#     contact = Contact.objects.filter( profile=profile)
#     return render(request, 'employee/cmp_profile.html',{
#         'data': profile,
#         'contact': contact
#         }) 
@employee_role_required
@login_required
def company_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    contact, created = Contact.objects.get_or_create(profile=profile)

    if request.method == 'POST':
        profile.first_name = request.POST.get('first_name')
        profile.job_title = request.POST.get('job_title')
        profile.location = request.POST.get('location')
        profile.establised_at = request.POST.get('establised_at') or None
        profile.total_employees = request.POST.get('total_employees') or None
        profile.save()

        contact.link1 = request.POST.get('link1')
        contact.save()

        return redirect('employer:company_profile')

    return render(request, 'employee/cmp_profile.html', {
        'data': profile,
        'contact': contact
    })


@employee_role_required
@login_required
def company_settings(request):
    user = User.objects.get(id=request.user.id)

    if request.method == 'POST':
        # Get profile update fields
        new_username = request.POST.get('company-name')
        new_email = request.POST.get('email')
        new_phone_raw = request.POST.get('phone')
        new_phone = new_phone_raw.replace("+880", "").strip() if new_phone_raw else None

        # Get password change fields
        current_password = request.POST.get('current-password')
        new_password = request.POST.get('new-password')
        confirm_password = request.POST.get('confirm-password')

        updated = False  # Track if profile updated
        password_updated = False  # Track if password updated

        # --- Profile Updates ---
        if new_username and new_username != user.username:
            if User.objects.exclude(id=user.id).filter(username=new_username).exists():
                messages.error(request, 'Username is already taken.')
                return redirect('employer:company_settings')
            else:
                user.username = new_username
                updated = True

        if new_email and new_email != user.email:
            if User.objects.exclude(id=user.id).filter(email=new_email).exists():
                messages.error(request, 'Email is already in use.')
                return redirect('employer:company_settings')
            else:
                user.email = new_email
                updated = True

        # if new_phone and str(user.phone_no) != new_phone:
        #     if User.objects.exclude(id=user.id).filter(phone_no=new_phone).exists():
        #         messages.error(request, 'Phone number is already in use.')
        #         return redirect('employer:company_settings')
        #     else:
        #         try:
        #             user.phone_no = int(new_phone)
        #             updated = True
        #         except ValueError:
        #             messages.error(request, 'Phone number must be numeric.')
        #             return redirect('employer:company_settings')

        # --- Password Change ---
        if current_password or new_password or confirm_password:
            if not (current_password and new_password and confirm_password):
                messages.error(request, 'All password fields are required.')
                return redirect('employer:company_settings')

            if not user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
                return redirect('employer:company_settings')

            if new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
                return redirect('employer:company_settings')

            user.set_password(new_password)
            password_updated = True

        # Save changes
        if updated or password_updated:
            user.save()
            if password_updated:
                update_session_auth_hash(request, user)  # Prevent logout
                messages.success(request, 'Password updated successfully.')
            if updated:
                messages.success(request, 'Profile updated successfully.')
        else:
            messages.info(request, 'No changes were made.')

        return redirect('employer:company_settings')

    return render(request, 'employee/cmp_settings.html', {'data': user})



@employee_role_required
@login_required
def company_messages(request):

    return render(request, 'employee/cmp_message.html') 


def view_job(request, job_id):
    job = get_object_or_404(Job, job_id=job_id)
    apl_cont = JobApplication.objects.filter(job=job).count()
    applicant = JobApplication.objects.filter(job=job).select_related('applicant').order_by('-applied_date')
    res_list = job.responsibilities.split("\n")
    req_list = job.requirements.split("\n")
    ben_list = job.benefits.split("\n")
    return render(request, 'employee/cmp_job_details.html', 
                  {'job': job,'res_list':res_list,'req_list':req_list,
                   'apl_cont':apl_cont,'ben_list':ben_list,'cand_list':applicant})


def delete_job(request, job_id):
    job = get_object_or_404(Job, job_id=job_id)
    job.delete()
    messages.success(request, "Job deleted successfully.")
    return redirect('employer:company_jobs')

def create_job(request):
    if request.method == 'POST':
        # Extract data from the request
        title = request.POST.get('title')
        location = request.POST.get('location')
        job_type = request.POST.get('job_type')
        salary_min = request.POST.get('salary_min')
        salary_max = request.POST.get('salary_max')
        exp_need = request.POST.get('exp_need')
        description = request.POST.get('description')
        responsibilities = request.POST.get('responsibilities')
        requirements = request.POST.get('requirements')
        benefits = request.POST.get('benefits')
        status = request.POST.get('status')
        category = request.POST.get('category')

        # Get the Company instance
        company = Company.objects.get(user=request.user)

        # Create and save the Job instance
        Job.objects.create(
            title=title,
            company=company,
            location=location,
            job_type=job_type,
            salary_min=salary_min,
            salary_max=salary_max,
            exp_need=exp_need,
            description=description,
            responsibilities=responsibilities,
            requirements=requirements,
            benefits=benefits,
            status=status,
            category=category
        )
        return redirect('employer:company_jobs')
    else:
        return render(request, 'employee/create_job.html')

def edit_job(request, job_id):
    job = get_object_or_404(Job, job_id=job_id)
    if request.method == 'POST':
        job.title = request.POST.get('title')
        job.location = request.POST.get('location')
        job.job_type = request.POST.get('job_type')
        job.salary_min = request.POST.get('salary_min')
        job.salary_max = request.POST.get('salary_max')
        job.exp_need = request.POST.get('exp_need')
        job.description = request.POST.get('description')
        job.responsibilities = request.POST.get('responsibilities')
        job.requirements = request.POST.get('requirements')
        job.benefits = request.POST.get('benefits')
        job.status = request.POST.get('status')
        job.category = request.POST.get('category')
        job.save()
        return redirect('employer:view_job', job_id=job.job_id)
    else:
        return render(request, 'employee/job_edit.html', {'job': job})
    
def schedule_interview(request):
    if request.method == 'POST':
        job_id = request.POST.get('job-select')
        profile_id = request.POST.get('candidate-select')  # Now selecting a Profile
        start_time_str = request.POST.get('date-range')
        duration_H = request.POST.get('duration_hours')
        duration_M = request.POST.get('duration_minutes')
        try:
            job = Job.objects.get(job_id=job_id)
            profile = Profile.objects.get(profile_id=profile_id)
            job_application = JobApplication.objects.get(job=job, applicant=profile)
            start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
            end_time = start_time + timedelta(hours=int(duration_H), minutes=int(duration_M))
            # print(start_time, end_time)

            # Check for conflicts within the same company
            company_conflicts = Interview.objects.filter(
                application__job__company=job.company,
                start_time__lt=end_time,  
                end_time__gt=start_time   
                ).exclude(end_time=start_time  
                ).exclude(start_time=end_time  
                ).exists()
            print(company_conflicts)
            if company_conflicts:
                messages.error(request, 'There is already an interview scheduled for this time priod.')
                return redirect('employer:schedule_interview')


            # If no conflicts, create the interview
            Interview.objects.create(
                application=job_application,
                start_time=start_time,
                end_time=end_time,
            )
            JobApplication.objects.filter(job=job, applicant=profile).update(is_scheduled=True)
            messages.success(request, 'Interview scheduled successfully.')
            return redirect('employer:schedule_interview')

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            print(e)
            return redirect('employer:schedule_interview')
        # return redirect('employer:schedule_interview')

    else:
        applications = JobApplication.objects.filter(job__company__user=request.user, is_scheduled=False, is_selected=True, is_interviewed=False).select_related('job', 'applicant')
        # jobs = Job.objects.filter(company__user=request.user) 
        interviews = Interview.objects.filter(application__job__company__user=request.user, application__is_interviewed=False, application__is_scheduled=True).order_by('start_time').select_related('application__job')
        now = timezone.now()
        # for app in applications:
        #     print("hello")
        #     print(f"Application ID: {app.application_id}")
        #     print(f"name: {app.applicant.first_name}")
        #     print(f"Job Title: {app.job.title}")
        #     print(f"Job id: {app.job.job_id}")
        return render(request, 'employee/interview_schedule.html', {
            # 'jobs': jobs,
            'interviews': interviews,
            'applications': applications,
            'now': now
        })

def schedule_delete(request, id):
    interview = get_object_or_404(Interview, id=id)
    JobApplication.objects.filter(application_id=interview.application.application_id).update(is_scheduled=False)
    interview.delete()
    messages.success(request, 'Interview deleted successfully.')
    return redirect('employer:schedule_interview')

def take_interview(request,id):
    interview = get_object_or_404(
        Interview.objects.select_related(
            'application__job',
            'application__job__company',
            'application__applicant',
            'application'
        ),id=id
    )
    # print(interview.id,interview.application.applicant.first_name,interview.application.applicant.last_name,interview.start_time)
    return render(request, 'employee/interview.html',{
        'interview':interview})

def interview_details(request,id):
    if request.method == 'POST': 
        start_time_str = request.POST.get('start_time')
        duration_H = request.POST.get('duration_hours')
        duration_M = request.POST.get('duration_minutes')
        try:
            # print(id)
            interview = Interview.objects.get(id=id)
            job = interview.application.job
            start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
            end_time = start_time + timedelta(hours=int(duration_H), minutes=int(duration_M))
            # print(start_time, end_time)

            # Check for conflicts within the same company
            company_conflicts = Interview.objects.filter(
                application__job__company=job.company,
                start_time__lt=end_time,  
                end_time__gt=start_time   
                ).exclude(end_time=start_time  
                ).exclude(start_time=end_time  
                ).exists()
            print(company_conflicts)
            if company_conflicts:
                messages.error(request, 'There is already an interview scheduled for this time priod.')
                return redirect('employer:interview_details',interview.id)

            Interview.objects.filter(id=id).update(
                start_time=start_time,
                end_time=end_time
            )
            messages.success(request, 'Interview scheduled successfully.')
            return redirect('employer:interview_details',id)

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            print(e)
            return redirect('employer:interview_details',id)
    interview = get_object_or_404(
        Interview.objects.select_related(
            'application__job',
            'application__job__company',
            'application__applicant',
            'application'
        ),id=id
    )
    contact = Contact.objects.get(profile=interview.application.applicant)
    # print(interview.id,interview.application.applicant.first_name,interview.application.applicant.last_name,interview.start_time)
    return render(request, 'employee/interview_details.html',{
        'interview':interview,
        'contact':contact,
        })


def interview_evaluation(request):
    interview = Interview.objects.filter(application__is_interviewed=True).annotate(
        ration=ExpressionWrapper(
            ((F("resume_ratings") + F("technical_score") + F("problem_solving_score") + F("communication_score")) * 100) / 35,
            output_field=FloatField()
        )
    ).order_by('start_time')
    return render(request, 'employee/candidate_evaluation.html',
                  {'interview':interview})

def interview_selection(request,id):
    interview = get_object_or_404(Interview,id=id)
    ration = ((interview.resume_ratings + interview.technical_score + interview.problem_solving_score + interview.communication_score)*100)/35
    return render(request, 'employee/selection.html', {
        'interview':interview,
        'total':round(ration,2)
        })

def view_resume(request,resume_id):
    application = get_object_or_404(JobApplication, application_id=resume_id)
    # print(application.application_id)
    # print("and",resume_id)
    # app= JobApplication.objects.all()
    # for a in app:
    #     print(a.application_id, a.job.title, a.applicant.first_name)
    if Interview.objects.filter(application=application).exists():
        interveiw = get_object_or_404(Interview, application=application)
    else:
        interveiw = None

    edu = application.applicant.educations.all()
    exp = application.applicant.experiences.all()
    skill = application.applicant.skills.all()
    prf = JobPreference.objects.get(profile=application.applicant)
    Cont = Contact.objects.get(profile=application.applicant)
    # print(application,interveiw,edu,exp,skill,prf,Cont)
    return render(request, 'employee/resume_view.html',{
        'intr':interveiw,
        'app': application,
        'pro': application.applicant,
        'edu':edu, 
        'exp':exp, 
        'skill':skill,
        'prf':prf,
        'cont':Cont
    })


@require_POST
def select_for_interview(request, candidate_id):
    
    candidate = JobApplication.objects.get(application_id=candidate_id)
    interview = Interview.objects.filter(application=candidate).exists()
    print(interview)
    try:
        if not interview:
            interview = Interview.objects.create(application=candidate)
        candidate.is_selected = 'True'
        candidate.save()
        return JsonResponse({'success': True})
    
    
    except JobApplication.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Candidate not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

def interview_complete(request,application_id):
    application = get_object_or_404(JobApplication, application_id=application_id)
    try:
        application.is_interviewed = True
        application.save()
        return JsonResponse({'success': True})
    
    except JobApplication.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Candidate not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
    

@require_POST
def resume_review(request, resume_id):   
    interveiw = Interview.objects.get(application__application_id=resume_id)
    try:
        data = json.loads(request.body)
        
        # Update rating
        rating = data.get('resume_ratings', 0)
        interveiw.resume_ratings = rating
        # Update evaluation notes
        # candidate.evaluation_notes = data.get('evaluation_notes', '')[:2000]  # Limit to 2000 chars
        interveiw.resume_comments = data.get('evaluation_notes', '')
        
        interveiw.save()
        return JsonResponse({'success': True})
    
    except interveiw.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Candidate not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
    


@require_POST
@csrf_exempt
def save_marks(request,id):
    try:
        technical_skills = int(request.POST.get('technical_skills', 0))
        communication = int(request.POST.get('communication', 0))
        problem_solving = int(request.POST.get('problem_solving', 0))
        
        # Validate marks
        if not all(0 <= mark <= 10 for mark in [technical_skills, communication, problem_solving]):
            return JsonResponse({'success': False, 'message': 'Marks must be between 0-10'})
        interview = Interview.objects.get(id=id)
        interview.technical_score = technical_skills
        interview.communication_score = communication
        interview.problem_solving_score = problem_solving
        interview.save()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@require_POST
@csrf_exempt
def save_feedback(request,id):
    try:
        feedback_notes = request.POST.get('feedback_notes', '')
        interview = Interview.objects.get(id=id)
        interview.feedback = feedback_notes
        interview.save()
        return JsonResponse({'success': True, 'value': feedback_notes})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    


