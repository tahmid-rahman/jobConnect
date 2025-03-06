from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from employer.models import Job,Company, JobApplication
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
