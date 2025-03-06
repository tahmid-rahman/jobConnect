from django.contrib import admin
from employer.models import Company,Job,JobApplication
# Register your models here.

admin.site.register(Company)
admin.site.register(Job)
admin.site.register(JobApplication)