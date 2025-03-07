from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from employer.models import Job,Company, JobApplication,Interview
from jobseeker.models import Profile,Skill
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
    active_jobs_count = Job.objects.filter(company__user=request.user, status="Active").count()
    applications = JobApplication.objects.filter(job__company__user=request.user, job__status="Active").count()

    return render(request, 'employee/employee_home.html', {'active_jobs_count': active_jobs_count, 'applications': applications}) 


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
            start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
            end_time = start_time + timedelta(hours=int(duration_H), minutes=int(duration_M))
            print(start_time, end_time)

            # Check for conflicts within the same company
            company_conflicts = Interview.objects.filter(
                company=job.company,
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exists()
            print(company_conflicts)
            # if company_conflicts:
            #     messages.error(request, 'There is already an interview scheduled for this time in the same company.')
            #     return redirect('employer:schedule_interview')

            # # Check for conflicts for the candidate (Profile)
            # candidate_conflicts = Interview.objects.filter(
            #     candidate=profile,
            #     start_time__lt=end_time,
            #     end_time__gt=start_time
            # ).exists()

            # if candidate_conflicts:
            #     messages.error(request, 'The candidate already has an interview scheduled at this time.')
            #     return redirect('employer:schedule_interview')

            # # If no conflicts, create the interview
            # Interview.objects.create(
            #     job=job,
            #     candidate=profile,  # Use the Profile instance
            #     start_time=start_time,
            #     end_time=end_time,
            #     company=job.company
            # )

            # messages.success(request, 'Interview scheduled successfully.')
            return redirect('employer:schedule_interview')

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('employer:schedule_interview')
        # return redirect('employer:schedule_interview')

    else:
        applications = JobApplication.objects.filter(job__company__user=request.user).select_related('job', 'applicant')
        jobs = Job.objects.filter(company__user=request.user)
        interviews = Interview.objects.filter(company__user=request.user).order_by('start_time').select_related('job')
        # for app in applications:
        #     print(f"Application ID: {app.application_id}")
        #     print(f"name: {app.applicant.first_name}")
        #     print(f"Job Title: {app.job.title}")
        #     print(f"Job id: {app.job.job_id}")
        return render(request, 'employee/interview_schedule.html', {
            'jobs': jobs,
            'interviews': interviews,
            'applications': applications
        })
