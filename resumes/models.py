from django.contrib.auth.models import User
from django.db import models


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="resumes")
    title = models.CharField(max_length=200, default="My Resume")
    file = models.FileField(upload_to="resumes/")
    extracted_text = models.TextField(blank=True)
    target_role = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.user.username})"


class ResumeAnalysis(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name="analysis")
    quality_score = models.PositiveSmallIntegerField(default=0)
    ats_score = models.PositiveSmallIntegerField(default=0)
    summary = models.TextField(blank=True)
    strengths = models.JSONField(default=list)
    improvements = models.JSONField(default=list)
    keyword_suggestions = models.JSONField(default=list)
    grammar_notes = models.JSONField(default=list)
    skills = models.JSONField(default=list)
    sections = models.JSONField(default=dict)
    raw_response = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Analysis for {self.resume.title}"


class JobMatch(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="job_matches")
    job_title = models.CharField(max_length=200)
    job_description = models.TextField()
    compatibility_score = models.PositiveSmallIntegerField(default=0)
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.job_title} match ({self.compatibility_score}%)"
