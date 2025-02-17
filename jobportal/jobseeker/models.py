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
