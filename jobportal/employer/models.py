from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Company(models.Model):
    company_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    # logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    logo = models.URLField(null=True, blank=True)
    description = models.TextField()
    
    def __str__(self):
        return self.name
    

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('Full-Time', 'Full-Time'),
        ('Part-Time', 'Part-Time'),
        ('Contract', 'Contract'),
        ('Internship', 'Internship')
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Draft', 'Draft'),
        ('Closed', 'Closed'),
    ]

    CATEGORY_CHOICES = [
        ('engineering', 'Engineering'),
        ('design', 'Design'),
        ('marketing', 'Marketing'),
    ]

    job_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Draft')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    def __str__(self):
        return f"{self.title} at {self.company.name}"
    
class JobApplication(models.Model):
    application_id = models.AutoField(primary_key=True)
    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    applicant = models.ForeignKey('jobseeker.Profile', on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    applied_date = models.DateTimeField(auto_now_add=True)
    is_selected = models.BooleanField(default=False, null=True, blank=True)
    is_scheduled = models.BooleanField(default=False, null=True, blank=True)
    is_interviewed = models.BooleanField(default=False, null=True, blank=True)
    def __str__(self):
        return f"{self.applicant.first_name} applied for {self.job.title}"
    

class Interview(models.Model):
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    resume_ratings = models.SmallIntegerField(
        default=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)])    
    technical_score = models.FloatField(
        default=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)])    
    communication_score = models.FloatField(
        default=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)])    
    problem_solving_score = models.FloatField(
        default=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)])    
    resume_comments = models.TextField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Interview with {self.application.applicant.first_name} for {self.application.job.title}"
    