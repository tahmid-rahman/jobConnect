from urllib.parse import urlencode
from django.contrib.auth import login, authenticate, logout, get_user_model, get_backends
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import requests

from jobportal import settings
from .models import CustomUser, OTP  # Import your CustomUser model
from jobseeker.models import Profile,JobPreference,Contact
from employer.models import Company
from .email import send_otp_email, send_welcome_email, send_waiting_email


# # User Registration
# def register(request):
#     if request.user.is_authenticated: 
#         if request.user.role == 'admin':
#             return redirect('adminpanel:admin_home')
#         elif request.user.role == 'user':
#             return redirect('jobseeker:dashboard')
#         elif request.user.role == 'employee':
#             return redirect('employee:employee_home')

#     if request.method == 'POST':
#         name = request.POST.get('name')
#         username = request.POST.get('username')
#         email = request.POST.get('email')
#         phone_no = request.POST.get('phone_no')
#         role = request.POST.get('role')
#         password1 = request.POST.get('password')
#         # password2 = request.POST.get('confirm_password')


#         # Check if email is already registered
#         if CustomUser.objects.filter(email=email).exists():
#             messages.error(request, "This email is already registered.")
#             return redirect('register')

#         # Check if username is already taken
#         if CustomUser.objects.filter(username=username).exists():
#             messages.error(request, "This username is already taken.")
#             return redirect('register')

#         # Create the user
#         if role == 'user' :
#             user = CustomUser.objects.create_user(
#                 name=name,
#                 username=username,
#                 email=email,
#                 phone_no=phone_no,
#                 role=role,
#                 status='approved',
#                 password=password1
#             )
#         else :
#             user = CustomUser.objects.create_user(
#                 name=name,
#                 username=username,
#                 email=email,
#                 phone_no=phone_no,
#                 role=role,
#                 password=password1
#             )

#         if user.role =="user" or user.role == "employee":
#             Profile.objects.create(
#                 user=user,
#                 first_name=name
#                 )
#             prf = Profile.objects.get(
#                 user = user
#                 )
#             JobPreference.objects.create(
#                 profile=prf
#                 )
#             Contact.objects.create(
#                 profile=prf
#             )
#             messages.success(request, "Registration successful.")
#             login(request, user)
#         elif user.role == "admin" :
#             Company.objects.create(user=user,name=name)
#             messages.success(request, "Registration successful.")
#             return redirect('login')

#         return redirect('login')

#     return render(request, 'accounts/registration.html')



def register(request):
    if request.user.is_authenticated: 
        if request.user.role == 'admin':
            return redirect('adminpanel:admin_home')
        elif request.user.role == 'user':
            return redirect('jobseeker:dashboard')
        elif request.user.role == 'employee':
            return redirect('employee:employee_home')

    if request.method == 'POST':
        # Check if this is OTP verification step
        if 'otp' in request.POST:
            return verify_otp(request)
        
        # Original registration form submission
        name = request.POST.get('name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_no = request.POST.get('phone_no')
        role = request.POST.get('role')
        password1 = request.POST.get('password')

        # Check if email is already registered
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return redirect('register')

        # Check if username is already taken
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "This username is already taken.")
            return redirect('register')

        # Create the user (but not active yet)
        user = CustomUser.objects.create_user(
            name=name,
            username=username,
            email=email,
            phone_no=phone_no,
            role=role,
            password=password1,
            is_active=False  # User won't be active until OTP verification
        )
        
        if user.role in ["user", "employee"]:
            Profile.objects.create(user=user, first_name=name)
            prf = Profile.objects.get(user=user)
            JobPreference.objects.create(profile=prf)
            Contact.objects.create(profile=prf)
        elif user.role == "admin":
            Company.objects.create(user=user, name=name)
        
        # Send OTP email
        send_otp_email(user)
        
        # Store user ID in session for verification step
        request.session['registering_user_id'] = user.id
        messages.info(request, "We've sent an OTP to your email. Please verify to complete registration.")
        return redirect('verify_otp')  # Create this view or modify to show OTP form

    return render(request, 'accounts/registration.html')

def verify_otp(request):
    if 'registering_user_id' not in request.session:
        messages.error(request, "Registration session expired. Please register again.")
        return redirect('register')
    
    user_id = request.session['registering_user_id']
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, "Invalid user. Please register again.")
        return redirect('register')
    
    if request.method == 'POST':
        otp_code = request.POST.get('otp')
        
        try:
            otp = OTP.objects.get(user=user, otp_code=otp_code, is_verified=False)
            if otp.is_expired():
                messages.error(request, "OTP has expired. Please request a new one.")
                return redirect('verify_otp')
            
            # Mark OTP as verified
            otp.is_verified = True
            otp.save()
            
            # Activate user
            user.is_active = True
            user.save()
            
            # Send welcome email
            if user.role == 'user':
                send_welcome_email(user)
            else :
                send_waiting_email(user)
                

            # Clean up session
            del request.session['registering_user_id']
            
            if user.role != 'user':
                messages.success(request, "Account verified successfully! you can login after verification.")

            # Log the user in
            if user.role == 'user':
                login(request, user)
                messages.success(request, f"Welcome, {user.username}! ")
                
            return redirect_based_on_role(request, user)
            # Redirect based on role
            # if user.role == 'admin':
            #     return redirect('adminpanel:admin_home')
            # elif user.role == 'user':
            #     return redirect('jobseeker:dashboard')
            # elif user.role == 'employee':
            #     return redirect('employee:employee_home')
                
        except OTP.DoesNotExist:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('verify_otp')
    
    # GET request - show OTP verification form
    return render(request, 'accounts/verify_otp.html', {'email': user.email})

def resend_otp(request):
    if 'registering_user_id' not in request.session:
        messages.error(request, "Registration session expired. Please register again.")
        return redirect('register')
    
    user_id = request.session['registering_user_id']
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, "Invalid user. Please register again.")
        return redirect('register')
    
    send_otp_email(user)
    messages.info(request, "New OTP has been sent to your email.")
    return redirect('verify_otp')


def user_login(request):
    if request.user.is_authenticated: 
        return redirect('landing_page')  # Redirect to landing page if already logged in

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




def google_auth_callback(request):
    if request.user.is_authenticated:
        return redirect_based_on_role(request,request.user)
    
    code = request.GET.get('code')
    error = request.GET.get('error')
    
    if error:
        messages.error(request, "Google authentication failed.")
        return redirect('login')
    
    # Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        'code': code,
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    
    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        tokens = response.json()
        
        if 'error' in tokens:
            messages.error(request, "Failed to authenticate with Google.")
            return redirect('login')
        
        # Get user info from Google
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {'Authorization': f"Bearer {tokens['access_token']}"}
        response = requests.get(userinfo_url, headers=headers)
        response.raise_for_status()
        user_info = response.json()
        
        # Check if user exists by google_id or email
        try:
            user = CustomUser.objects.get(google_id=user_info['sub'])
            if user.role == 'admin' and user.status == 'approved':
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}! ")
            elif user.role == 'user':
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}! ")
            elif user.role == 'employee' and user.status == 'approved':
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}! ")
            elif user.status == 'pending':
                messages.error(request, "Your account is pending for approval. Please wait for approval.")
                return redirect('login')
            return redirect_based_on_role(request, user)
        except CustomUser.DoesNotExist:
            try:
                # Check if user exists by email (existing local account)
                user = CustomUser.objects.get(email=user_info['email'])
                user.google_id = user_info['sub']
                user.email_verified = user_info.get('email_verified', False)
                user.save()
                return redirect_based_on_role(request, user)
            except CustomUser.DoesNotExist:
                # New user - store data in session for role selection
                request.session['google_user_data'] = {
                    'google_id': user_info['sub'],
                    'email': user_info['email'],
                    'email_verified': user_info.get('email_verified', False),
                    'name': user_info.get('name', ''),
                    'given_name': user_info.get('given_name', ''),
                    'family_name': user_info.get('family_name', ''),
                    'picture': user_info.get('picture')
                }
                return redirect('select_role')
                
    except requests.RequestException as e:
        messages.error(request, f"Error connecting to Google: {str(e)}")
        return redirect('login')

def select_role(request):
    if not request.session.get('google_user_data'):
        return redirect('login')
    
    google_data = request.session['google_user_data']
    
    if request.method == 'POST':
        role = request.POST.get('role')
        
        if role not in ['user', 'employee', 'admin']:
            messages.error(request, "Invalid role selected.")
            return redirect('select_role')
        
        # Create username from email
        username = google_data['email'].split('@')[0]
        while CustomUser.objects.filter(username=username).exists():
            username = f"{username}_{CustomUser.objects.filter(username__startswith=username).count()}"
        
        
        # Create the user
        user = CustomUser.objects.create_user(
            name=google_data['name'],
            username=username,
            email=google_data['email'],
            google_id=google_data['google_id'],
            email_verified=google_data['email_verified'],
            role=role,
            status='approved' if role == 'user' else 'pending'
        )
        
        # Create profile
        profile = Profile.objects.create(
            user=user,
            first_name=google_data.get('given_name', ''),
            last_name=google_data.get('family_name', ''),
            google_picture_url=google_data.get('picture')
        )
        
        # Create role-specific models
        if role == 'user':
            JobPreference.objects.create(profile=profile)
            Contact.objects.create(profile=profile)
            messages.success(request, "Job seeker account created successfully!")
        elif role == 'employee':
            Company.objects.create(user=user, name=google_data['name'])
            messages.success(request, "Employer account created! Waiting for approval.")
        elif role == 'admin':
            Company.objects.create(user=user, name=google_data['name'])
            messages.success(request, "Admin account created! Waiting for approval.")
        
        # Clean up session
        del request.session['google_user_data']
        
        # Log in and redirect
        if role == 'user':
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f"Welcome, {user.username}!")

        return redirect_based_on_role(request, user)
    
    return render(request, 'accounts/select_role.html')

def get_google_auth_url(request):
    if request.user.is_authenticated:
        return JsonResponse({'error': 'Already authenticated'}, status=400)
    
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'online',
        'prompt': 'select_account',
    }
    auth_url = f"{base_url}?{urlencode(params)}"
    return JsonResponse({'url': auth_url})

def redirect_based_on_role(request, user):
    # if user.role == 'admin' and user.status == 'approved':
    #     return redirect('adminpanel:admin_home')
    # elif user.role == 'user':
    #     return redirect('jobseeker:dashboard')
    # elif user.role == 'employee' and user.status == 'approved':
    #     return redirect('employer:company_dashboard')
    # if user.role in ['employee', 'admin'] and user.status == 'pending':
    #     messages.error(request, "Your account is pending for approval. Please wait for approval.")
    return redirect('landing_page')