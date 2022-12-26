from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from home.models import *


class EducationAdmin(SummernoteModelAdmin):

    list_display = ["school_name", "gpa", "city", "state", "country", "start_date", "end_date"]
    search_fields = ["school_name", "city", "state", "country", "coursework"]
    summernote_fields = ['address', 'coursework', 'description']


class WorkAdmin(SummernoteModelAdmin):

    list_display = ["company_name", "designation", "city", "state", "country", "start_date", "end_date"]
    search_fields = ["company_name", "city", "state", "country", "designation", "skills_used"]
    summernote_fields = ['address', 'skills_used', 'description']


class ProjectAdmin(SummernoteModelAdmin):

    list_display = ["project_title", "github_link", "start_date", "end_date"]
    search_fields = ["project_title"]
    list_filter = ["has_paper", "has_patent"]
    summernote_fields = ['skills_used', 'description']


admin.site.register(Education, EducationAdmin)
admin.site.register(Work, WorkAdmin)
admin.site.register(Project, ProjectAdmin)