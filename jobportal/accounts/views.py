from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser  # Import your CustomUser model
from jobseeker.models import Profile,JobPreference,Contact
from employer.models import Company

from accounts import models

# User Registration
def register(request):
    if request.user.is_authenticated: 
        if request.user.role == 'admin':
            return redirect('adminpanel:admin_home')
        elif request.user.role == 'user':
            return redirect('jobseeker:dashboard')
        elif request.user.role == 'employee':
            return redirect('employee:employee_home')

    if request.method == 'POST':
        name = request.POST.get('name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_no = request.POST.get('phone_no')
        role = request.POST.get('role')
        password1 = request.POST.get('password')
        # password2 = request.POST.get('confirm_password')


        # Check if email is already registered
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return redirect('register')

        # Check if username is already taken
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "This username is already taken.")
            return redirect('register')

        # Create the user
        if role == 'user' :
            user = CustomUser.objects.create_user(
                name=name,
                username=username,
                email=email,
                phone_no=phone_no,
                role=role,
                status='approved',
                password=password1
            )
        else :
            user = CustomUser.objects.create_user(
                name=name,
                username=username,
                email=email,
                phone_no=phone_no,
                role=role,
                password=password1
            )

        if user.role =="user" or user.role == "employee":
            Profile.objects.create(
                user=user,
                first_name=name
                )
            prf = Profile.objects.get(
                user = user
                )
            JobPreference.objects.create(
                profile=prf
                )
            Contact.objects.create(
                profile=prf
            )
            messages.success(request, "Registration successful.")
            login(request, user)
        elif user.role == "admin" :
            Company.objects.create(user=user,name=name)
            messages.success(request, "Registration successful.")
            return redirect('login')

        return redirect('login')

    return render(request, 'accounts/registration.html')



def user_login(request):
    if request.user.is_authenticated: 
        if request.user.role == 'admin':
            return redirect('adminpanel:admin_home')
        elif request.user.role == 'user':
            return redirect('jobseeker:dashboard')
        elif request.user.role == 'employee':
            return redirect('employee:employee_home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email, password)

        # Authenticate using email and password
        user = authenticate(request, username=email, password=password)
        if user is not None:
            print('success')
           

            # Redirect based on user role
            if user.role == 'admin':
                if user.status == 'pending':
                    messages.error(request, "Your account is pending approval. Please wait for approval.")
                    return redirect('login')
                else:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.username}! ")
                    return redirect('adminpanel:admin_home')
            elif user.role == 'user':
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}! ")
                return redirect('jobseeker:dashboard')
            elif user.role == 'employee':
                if user.status == 'pending':
                    messages.error(request, "Your account is pending for approval. Please wait approval. You will be notified through Email after confirmation.")
                    return redirect('login')
                else:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.username}! ")
                    return redirect('employer:company_dashboard')
            else:
                return redirect('login')  # Fallback if role is undefined
        else:
            print('failed')
            messages.error(request, "Invalid email or password.")
    
    return render(request, 'accounts/login.html')



@login_required
def user_logout(request):
    logout(request)
    print('logout success')
    messages.success(request, "You have successfully logged out.")
    return redirect('landing_page')  # Redirect to login page after logout


@login_required
def get_users(request):
    search = request.GET.get('search', '')
    users = CustomUser.objects.exclude(id=request.user.id)
    
    if search:
        users = (
            CustomUser.objects.filter(username__icontains=search) |
            CustomUser.objects.filter(profile__first_name__icontains=search) |
            CustomUser.objects.filter(profile__last_name__icontains=search)
        )

    users = users.select_related('profile')[:20]  # Limit to 20 results
    
    data = []
    for user in users:
        name = ""
        if hasattr(user, 'profile'):
            if user.profile.first_name or user.profile.last_name:
                name = f"{user.profile.first_name or ''} {user.profile.last_name or ''}".strip()
        
        if not name:
            name = user.username
            
        data.append({
            'id': user.id,
            'name': name,
            'username': user.username,
            'picture': user.profile.profile_picture.url if hasattr(user, 'profile') and user.profile.profile_picture else None
        })
    
    return JsonResponse(data, safe=False)