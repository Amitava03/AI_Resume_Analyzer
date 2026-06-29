from django.contrib import admin

from .models import InterviewQuestion, InterviewResponse, InterviewSession


class InterviewQuestionInline(admin.TabularInline):
    model = InterviewQuestion
    extra = 0


@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ("target_role", "user", "difficulty", "created_at")
    inlines = [InterviewQuestionInline]


@admin.register(InterviewResponse)
class InterviewResponseAdmin(admin.ModelAdmin):
    list_display = ("question", "overall_score", "created_at")
