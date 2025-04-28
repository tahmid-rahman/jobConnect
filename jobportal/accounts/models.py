from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import random
import string
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
# User = get_user_model()

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required.")
        if not email:
            raise ValueError("Email is required.")
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    phone_no = models.IntegerField(max_length=15,null=True,blank=True)
    role = models.CharField(max_length=50, choices=[
        ('admin', 'Admin'),
        ('user', 'User'),
        ('employee', 'Employee'),
    ], default='user')
    status = models.CharField(max_length=50, choices=[
        ('approved','Approved'),
        ('pending', 'Pending'),
    ],default='pending')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    google_id = models.CharField(max_length=255, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']

    def __str__(self):
        return self.username


class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.email} - {self.otp_code}"
    
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)
    
    @classmethod
    def generate_otp(cls, user):
        # Delete any existing OTPs for this user
        cls.objects.filter(user=user).delete()
        
        # Generate a 6-digit numeric OTP
        otp_code = ''.join(random.choices(string.digits, k=6))
        return cls.objects.create(user=user, otp_code=otp_code)