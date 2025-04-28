from django.shortcuts import render,redirect


def landing_page(request):
    if request.user.is_authenticated: 
        if request.user.role == 'admin':
            if request.user.status == 'approved':
                return redirect('adminpanel:admin_home')
            # else:
            #     return redirect('adminpanel:admin_home')
        elif request.user.role == 'user':
            return redirect('jobseeker:dashboard')
        elif request.user.role == 'employee':
            if request.user.status == 'approved':
                return redirect('employer:company_dashboard')
    return render(request, 'components/landing.html')


def custom_404_view(request, exception):
    return redirect('')