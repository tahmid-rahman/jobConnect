from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Job,Company,Profile,JobPreference
from accounts.models import CustomUser


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
    print(request.path)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) 
    return render(request, 'jobseeker/user_home.html',{'page_obj': page_obj}) 


@user_role_required
@login_required   
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
    
@user_role_required
@login_required   
def company_detail(request,company_id):
    compa = Company.objects.get(company_id = company_id)
    jobs = Job.objects.filter(company=company_id)
    paginator = Paginator(jobs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) 
    return render(request, 'jobseeker/company_details.html',{'compa':compa,'page_obj':page_obj}) 
    
    
@user_role_required
@login_required
def setting(request):
    return render(request, 'jobseeker/settings.html') 

@user_role_required
@login_required
def profile(request):
    pro = Profile.objects.get(user=request.user)
    edu = pro.educations.all()
    exp = pro.experiences.all()
    skill = pro.skills.all()
    prf = JobPreference.objects.get(profile=pro)
    # print(pro.first_name)
    # for e in exp :
    #     print(e.job_title)
    
    return render(request, 'jobseeker/profile.html',{'pro': pro,'edu':edu, 'exp':exp, 'skill':skill,'prf':prf}) 

@user_role_required
@login_required
def tips(request):
    return render(request, 'jobseeker/tips.html') 
    
@user_role_required
@login_required
def insight(request):
    return render(request, 'jobseeker/salary_insight.html') 

@user_role_required
@login_required
def resume_tips(request):
    return render(request, 'jobseeker/10Tips.html') 

@user_role_required
@login_required
def tips2(request):
    return render(request, 'jobseeker/tips2.html') 

@user_role_required
@login_required
def tips3(request):
    return render(request, 'jobseeker/tips3.html') 
    