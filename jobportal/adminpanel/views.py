from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def admin_role_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.role == 'user':
            # messages.error(request, "You are not authorized to view this page.")
            return redirect('jobseeker:dashboard')
        elif request.user.role == 'employee':
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_role_required
@login_required
def admin_home(request):
    return render(request, 'admin/admin_dashboard.html') 


@admin_role_required
@login_required
def user_management(request):
    return render(request, 'admin/user_management.html')


@admin_role_required
@login_required
def job_management(request):
    return render(request, 'admin/jobpostings_control.html')

@admin_role_required
@login_required
def content_management(request):
    return render(request, 'admin/content_management.html')

@admin_role_required
@login_required
def feedback_analytics(request):
    return render(request, 'admin/feedback_analytics.html')

@admin_role_required
@login_required
def platform_security(request):
    return render(request, 'admin/platform_security.html')

@admin_role_required
@login_required
def settings(request):
    return render(request, 'admin/admin_settings.html')

@admin_role_required
@login_required
def site_configuration(request):
    return render(request, 'admin/admin_settings.html')
