from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def user_role_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.role == 'admin':
            messages.error(request, "You are not authorized to view this page.")
            return redirect('adminpanel:admin_home')
        return view_func(request, *args, **kwargs)
    return wrapper
@user_role_required
@login_required
def dashboard(request):
    return render(request, 'jobseeker/user_home.html') 
    
    