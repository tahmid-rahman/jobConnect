from django.shortcuts import render,redirect


def landing_page(request):
    if request.user.is_authenticated: 
        if request.user.role == 'admin':
            return redirect('adminpanel:admin_home')
        elif request.user.role == 'user':
            return redirect('jobseeker:dashboard')
        elif request.user.role == 'employee':
            return redirect('employee:employee_home')
    return render(request, 'components/landing.html')


def custom_404_view(request, exception):
    return redirect('')