# accounts/email.py
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import OTP

def send_otp_email(user):
    """
    Generates and sends an OTP email to the user
    """
    # Generate OTP
    otp = OTP.generate_otp(user)
    
    # Prepare email content
    subject = 'Your OTP for Account Verification'
    html_message = render_to_string('accounts/otp_email.html', {
        'name': user.name,
        'otp': otp.otp_code,
    })
    plain_message = strip_tags(html_message)
    
    # Send email
    send_mail(
        subject,
        plain_message,
        None,  # Uses DEFAULT_FROM_EMAIL from settings
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_welcome_email(user):
    """
    Example of another email function you might want to add
    """
    subject = 'Welcome to Our Platform!'
    html_message = render_to_string('accounts/welcome_email.html', {
        'name': user.name,
        'email': user.email,
        'username': user.username,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        None,
        [user.email],
        html_message=html_message,
    )

def send_waiting_email(user):
    """
    Example of another email function you might want to add
    """
    subject = 'Your Account is Pending Approval'
    html_message = render_to_string('accounts/waiting_email.html', {
        'name': user.name,
        'email': user.email,
        'company_name': 'JobConnect',
        'review_timeframe': '7-10 business days',
        'submission_date': timezone.now().strftime('%Y-%m-%d'),
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        None,
        [user.email],
        html_message=html_message,
    )