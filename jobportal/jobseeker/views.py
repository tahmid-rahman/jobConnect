from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Job,Company


def user_role_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'user':
            messages.error(request, "You are not authorized to view this page.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
@user_role_required
@login_required
def dashboard(request):
    jobs = Job.objects.all().order_by('-posted_date') 
    paginator = Paginator(jobs, 3)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) 
    return render(request, 'jobseeker/user_home.html',{'page_obj': page_obj}) 
    
def job_detail(request,job_id):
    job = Job.objects.get(job_id = job_id)
    comp = Company.objects.get(company_id = job.company.company_id)
    res_list = job.responsibilities.split("\n")
    req_list = job.requirements.split("\n")
    ben_list = job.benefits.split("\n")
    return render(request, 'jobseeker/job_details.html',{'job': job, 'comp': comp,'res_list':res_list,'req_list':req_list,'ben_list':ben_list}) 
    
@user_role_required
@login_required
def company_view(request):
    comp =  Company.objects.all() 
    paginator = Paginator(comp, 6)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) 
    return render(request, 'jobseeker/company.html',{'page_obj': page_obj}) 
    
    