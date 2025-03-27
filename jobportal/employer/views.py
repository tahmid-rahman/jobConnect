from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from employer.models import Job,Company, JobApplication,Interview
from jobseeker.models import Profile,Skill,Contact,JobPreference
from django.db.models import Count,Subquery,Prefetch





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

@employee_role_required
@login_required
def company_profile(request):
    return render(request, 'employee/cmp_profile.html') 

@employee_role_required
@login_required
def company_settings(request):
    return render(request, 'employee/cmp_settings.html') 


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
        interviews = Interview.objects.filter(application__job__company__user=request.user, application__is_interviewed=False).order_by('start_time').select_related('application__job')
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
    interview = Interview.objects.filter(application__is_interviewed=True).order_by('start_time')
    return render(request, 'employee/candidate_evaluation.html',
                  {'interview':interview})

def interview_selection(request,id):
    interview = get_object_or_404(Interview,id=id)
    return render(request, 'employee/selection.html',
                  {'interview':interview})

def view_resume(request,id):
    application = get_object_or_404(JobApplication, application_id=id)
    edu = application.applicant.educations.all()
    exp = application.applicant.experiences.all()
    skill = application.applicant.skills.all()
    prf = JobPreference.objects.get(profile=application.applicant)
    Cont = Contact.objects.get(profile=application.applicant)
    return render(request, 'employee/resume_view.html',{
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
    try:
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
    