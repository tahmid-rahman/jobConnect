from django.contrib import admin

from .models import Job,Company
from .models import Profile, Experience, Education, Resume, JobPreference, Skill

class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 1

class EducationInline(admin.TabularInline):
    model = Education
    extra = 1

class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'job_title', 'location')
    search_fields = ('first_name', 'last_name', 'job_title', 'location')
    inlines = [ExperienceInline, EducationInline, SkillInline]

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Resume)
admin.site.register(JobPreference)


# Register your models here.
admin.site.register(Job)
admin.site.register(Company)

