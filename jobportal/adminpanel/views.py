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
    return render(request, 'admin/admin_home.html') 
    
    