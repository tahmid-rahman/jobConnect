from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth import update_session_auth_hash
from .models import Job,Company,Profile,JobPreference,Experience,Education,Skill,Contact
from accounts.models import CustomUser
from employer.models import JobApplication,Interview


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
    paginator = Paginator(jobs, 6)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) 
    return render(request, 'jobseeker/user_home.html',{'page_obj': page_obj}) 


@user_role_required
@login_required   
def job_detail(request,job_id):
    job = Job.objects.get(job_id = job_id)
    application = JobApplication.objects.filter(job=job).count()
    applied =  JobApplication.objects.filter(job=job, applicant=Profile.objects.get(user=request.user)).exists()
    comp = Company.objects.get(company_id = job.company.company_id)
    res_list = job.responsibilities.split("\n")
    req_list = job.requirements.split("\n")
    ben_list = job.benefits.split("\n")
    return render(request, 'jobseeker/job_details.html',
                  {'job': job, 'comp': comp,'res_list':res_list,'req_list':req_list,
                   'ben_list':ben_list,'app_cont':application,'applied':applied}) 
    
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
def update_account(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        uname = request.POST.get('username')
        email = request.POST.get('email')
        p_no = request.POST.get('phone_no')

    if CustomUser.objects.filter(email=email).exclude(id=request.user.id).exists():
        messages.error(request, f"This '{email}' email is already registered.")
        return redirect('jobseeker:setting') 
    
    if CustomUser.objects.filter(username=uname).exclude(id=request.user.id).exists():
        messages.error(request, f"This '{uname}' username is already registered.")
        return redirect('jobseeker:setting') 
    
    data = request.user
    data.name = name
    data.username = uname
    data.email = email
    data.phone_no = p_no
    data.save()
    messages.error(request, "Updated Successfully.")

    return redirect('jobseeker:setting') 

@user_role_required
@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_new_password = request.POST['confirm_new_password']

        if new_password != confirm_new_password:
            messages.error(request, "New passwords do not match.")
            return redirect('jobseeker:setting')

        user = request.user
        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect('jobseeker:setting')

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)  # Keep the user logged in
        messages.success(request, "Your password has been successfully updated.")
        return redirect('jobseeker:setting')

    return redirect('jobseeker:setting')

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
def update_profile(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        job_title = request.POST.get('job_title')
        location = request.POST.get('location')

        # Assuming the profile is linked to the user
        pro = request.user.profile
        pro.first_name = first_name
        pro.last_name = last_name
        pro.job_title = job_title
        pro.location = location
        pro.save()

        return redirect('jobseeker:profile') 

    return render(request, 'jobseeker/profile.html')


@login_required
@user_role_required
def update_about_me(request):
    if request.method == 'POST':
        about_me = request.POST.get('about_me')

        pro = request.user.profile
        pro.about_me = about_me
        pro.save()

        return redirect('jobseeker:profile')  # Redirect to the profile page after updating

    return render(request, 'jobseeker/profile.html')

@user_role_required
@login_required
def add_work_experience(request):
    if request.method == 'POST':
        job_title = request.POST.get('job_title')
        company_name = request.POST.get('company_name')
        location = request.POST.get('location')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        description = request.POST.get('description')

        prf = Profile.objects.get(user =request.user)

        Experience.objects.create(
            profile= prf,
            job_title=job_title,
            company_name=company_name,
            location=location,
            start_date=start_date,
            end_date=end_date if end_date else None,
            description=description
        )

    return redirect('jobseeker:profile')


@user_role_required
@login_required
def update_work_experience(request, id):
    prf = Profile.objects.get(user =request.user)

    if request.method == 'POST':
        work_experience = Experience.objects.get(exp_id=id, profile= prf)
        work_experience.job_title = request.POST.get('job_title')
        work_experience.company_name = request.POST.get('company_name')
        work_experience.location = request.POST.get('location')
        work_experience.start_date = request.POST.get('start_date')
        work_experience.end_date = request.POST.get('end_date')
        work_experience.description = request.POST.get('description')
        work_experience.save()

    return redirect('jobseeker:profile')


@user_role_required
@login_required
def delete_work_experience(request, id):
    prf = Profile.objects.get(user =request.user)
    if request.method == 'POST':
        work_experience = Experience.objects.get(exp_id=id, profile= prf)
        work_experience.delete()

    return redirect('jobseeker:profile')

@user_role_required
@login_required
def add_education(request):
    if request.method == 'POST':
        degree = request.POST.get('degree')
        school = request.POST.get('school')
        location = request.POST.get('location')
        graduation_date = request.POST.get('graduation_date')
        prf = Profile.objects.get(user =request.user)
        Education.objects.create(
            profile= prf,
            degree=degree,
            school=school,
            location=location,
            graduation_date=graduation_date
        )

    return redirect('jobseeker:profile')

@user_role_required
@login_required
def update_education(request, id):
    if request.method == 'POST':
        education = Education.objects.get(edu_id=id, profile=Profile.objects.get(user=request.user))
        education.degree = request.POST.get('degree')
        education.school = request.POST.get('school')
        education.location = request.POST.get('location')
        education.graduation_date = request.POST.get('graduation_date')
        education.save()

    return redirect('jobseeker:profile')
@user_role_required
@login_required
def delete_education(request, id):
    if request.method == 'POST':
        education = Education.objects.get(edu_id=id, profile=Profile.objects.get(user=request.user))
        education.delete()

    return redirect('jobseeker:profile')


@user_role_required
@login_required
def update_job_preferences(request):
    if request.method == 'POST':
        job_type = request.POST.get('job_type')
        preferred_location = request.POST.get('preferred_location')
        salary_expectation = request.POST.get('salary_expectation')


        job_pre = JobPreference.objects.get(profile=Profile.objects.get(user=request.user))
        job_pre.job_type = job_type
        job_pre.preferred_location = preferred_location
        job_pre.salary_expectation = salary_expectation
        job_pre.save()

    return redirect('jobseeker:profile')


@user_role_required
@login_required
def add_skills(request):
    if request.method == 'POST':
        skill_name = request.POST.get('skill_name')

        # Create a new Skill instance linked to the current user's profile
        Skill.objects.create(
            profile=request.user.profile,
            name=skill_name
        )

    return redirect('jobseeker:profile')


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
    
@login_required
def upload_profile_picture(request):
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        user = request.user
        user.profile.profile_picture = request.FILES['profile_picture']
        user.profile.save()
        messages.success(request, "Upload successful!")
    else:
        messages.error(request, "Error uploading image.")

    return redirect('jobseeker:profile')



@login_required
def remove_skill(request, skill_id):
    if request.method == 'POST':
        pro = Profile.objects.get(user=request.user)
        skill = pro.skills.filter(id=skill_id).first()
        print(skill)
        try:
            skill.delete()
            messages.success(request, "Skill removed successfully.")
        except Exception as e:
            messages.error(request, f"Failed to remove skill: {str(e)}")
            
        return redirect('jobseeker:profile')  
    
    messages.error(request, "Invalid request method.")
    return redirect('jobseeker:profile')



@login_required
def resume_build(request,id):
    pro = Profile.objects.get(profile_id=id)
    edu = pro.educations.all()
    exp = pro.experiences.all()
    skill = pro.skills.all()
    prf = JobPreference.objects.get(profile=pro)
    Cont = Contact.objects.get(profile=pro)
    return render(request, 'jobseeker/resume_tem1.html',{'pro': pro,'edu':edu, 'exp':exp, 'skill':skill,'prf':prf,'cont':Cont})


def apply_job(request, id):
    if not JobApplication.objects.filter(job=Job.objects.get(job_id=id), applicant=Profile.objects.get(user=request.user)).exists():
        JobApplication.objects.create(
            job=Job.objects.get(job_id=id),
            applicant=Profile.objects.get(user=request.user)
        )
        application = JobApplication.objects.get(job=Job.objects.get(job_id=id), applicant=Profile.objects.get(user=request.user))
        interview = Interview.objects.filter(application=application).exists()
        if not interview:
            interview = Interview.objects.create(application=application)
        messages.success(request, "Application submitted successfully.")
    else:
        messages.error(request, "You have already applied for this job.")
    return redirect('jobseeker:job_detail',job_id=id)