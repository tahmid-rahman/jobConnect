from django.db import models
from accounts.models import CustomUser
from employer.models import Company,Job




class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    profile_id = models.AutoField(primary_key=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True,default='profile_pics/profile_1.png')
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    about_me = models.TextField( blank=True, null=True)
    establised_at = models.DateField(blank=True, null=True)
    total_employees = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Experience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='experiences')
    exp_id =models.AutoField(primary_key=True)
    job_title = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='educations')
    edu_id =models.AutoField(primary_key=True)
    degree = models.CharField(max_length=100)
    school = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    graduation_date = models.DateField()

    def __str__(self):
        return f"{self.degree} from {self.school}"

class Resume(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='resume')
    # resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)
    resume_file = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Resume of {self.profile}"

class JobPreference(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='job_preferences')
    job_type = models.CharField(max_length=50)
    preferred_location = models.CharField(max_length=100)
    salary_expectation = models.CharField(max_length=50)

    def __str__(self):
        return f"Job Preferences of {self.profile}"

class Skill(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='skills')
    # skill_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
class Contact(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='contacts')
    contact_id = models.AutoField(primary_key=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.IntegerField(blank=True, null=True)
    link1 = models.URLField(blank=True, null=True)
    link2 = models.URLField(blank=True, null=True)
    link3 = models.URLField(blank=True, null=True)


    def __str__(self):
        return f"Contact of {self.profile}"

