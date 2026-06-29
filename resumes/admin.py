from django.contrib import admin

from .models import JobMatch, Resume, ResumeAnalysis


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "target_role", "created_at")
    search_fields = ("title", "user__username", "target_role")


@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ("resume", "quality_score", "ats_score", "created_at")


@admin.register(JobMatch)
class JobMatchAdmin(admin.ModelAdmin):
    list_display = ("job_title", "resume", "compatibility_score", "created_at")
