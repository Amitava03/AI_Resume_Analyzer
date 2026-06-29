from django.contrib.auth.models import User
from django.db import models

from resumes.models import Resume


class InterviewSession(models.Model):
    DIFFICULTY_CHOICES = [
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="interview_sessions")
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, blank=True)
    target_role = models.CharField(max_length=200)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default="medium")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.target_role} session ({self.user.username})"


class InterviewQuestion(models.Model):
    QUESTION_TYPES = [
        ("technical", "Technical"),
        ("behavioral", "Behavioral"),
        ("hr", "HR"),
    ]

    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name="questions")
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    question_text = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.question_type}: {self.question_text[:60]}"


class InterviewResponse(models.Model):
    question = models.OneToOneField(InterviewQuestion, on_delete=models.CASCADE, related_name="response")
    answer_text = models.TextField()
    confidence_score = models.PositiveSmallIntegerField(default=0)
    relevance_score = models.PositiveSmallIntegerField(default=0)
    completeness_score = models.PositiveSmallIntegerField(default=0)
    overall_score = models.PositiveSmallIntegerField(default=0)
    feedback = models.TextField(blank=True)
    suggestions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Response to Q{self.question_id}"
