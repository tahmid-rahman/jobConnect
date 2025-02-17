from django.db import models

class Company(models.Model):
    company_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    # logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    logo = models.URLField(null=True, blank=True)
    description = models.TextField()
    
    def __str__(self):
        return self.name

class Job(models.Model):
    job_id = models.AutoField(primary_key=True)
    JOB_TYPE_CHOICES = [
        ('Full-Time', 'Full-Time'),
        ('Part-Time', 'Part-Time'),
        ('Contract', 'Contract'),
        ('Internship', 'Internship')
    ]

    title = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    posted_date = models.DateTimeField(auto_now_add=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2)
    applications = models.IntegerField(default=0)
    exp_need = models.IntegerField(default=0)
    description = models.TextField()
    responsibilities = models.TextField()
    requirements = models.TextField()
    benefits = models.TextField()
    
    def __str__(self):
        return f"{self.title} at {self.company.name}"
    

    from django.db import models

from accounts.models import CustomUser

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    profile_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    about_me = models.TextField( blank=True, null=True)
    # profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Experience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='experiences')
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
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

