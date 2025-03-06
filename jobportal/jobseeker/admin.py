from django.contrib import admin

from .models import Profile, Experience, Education, Resume, JobPreference, Skill, Contact

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
admin.site.register(Contact)


# Register your models here.

