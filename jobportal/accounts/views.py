from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser  # Import your CustomUser model
from jobseeker.models import Profile,JobPreference

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
        user = CustomUser.objects.create_user(
            name=name,
            username=username,
            email=email,
            phone_no=phone_no,
            role=role,
            password=password1
        )
        Profile.objects.create(user=user)
        prf = Profile.objects.get(user = user)
        JobPreference.objects.create(profile=prf)
        # Log the user in immediately after registration
        login(request, user)
        messages.success(request, "Registration successful.")
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
            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")

            # Redirect based on user role
            if user.role == 'admin':
                return redirect('adminpanel:admin_home')
            elif user.role == 'user':
                return redirect('jobseeker:dashboard')
            elif user.role == 'employee':
                return redirect('employee:employee_home')
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
