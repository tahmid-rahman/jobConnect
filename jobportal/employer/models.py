from django.db import models
# Create your models here.
class Company(models.Model):
    company_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
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

    def __str__(self):
        return f"{self.applicant.first_name} applied for {self.job.title}"
    

class Interview(models.Model):
    candidate = models.ForeignKey('jobseeker.Profile', on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return f"Interview with {self.candidate.first_name} for {self.job.title}"