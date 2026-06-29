from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import render

from interviews.models import InterviewResponse, InterviewSession
from resumes.models import JobMatch, Resume, ResumeAnalysis


@login_required
def home(request):
    resumes = Resume.objects.filter(user=request.user)
    latest_resume = resumes.first()
    latest_analysis = None
    if latest_resume:
        latest_analysis = getattr(latest_resume, "analysis", None)

    interview_sessions = InterviewSession.objects.filter(user=request.user)
    response_stats = InterviewResponse.objects.filter(
        question__session__user=request.user
    ).aggregate(avg_score=Avg("overall_score"))

    recent_matches = JobMatch.objects.filter(resume__user=request.user)[:3]
    all_skills: set[str] = set()
    for analysis in ResumeAnalysis.objects.filter(resume__user=request.user):
        all_skills.update(analysis.skills or [])

    career_recommendations = _build_career_recommendations(all_skills, latest_resume)

    context = {
        "resume_count": resumes.count(),
        "latest_resume": latest_resume,
        "latest_analysis": latest_analysis,
        "session_count": interview_sessions.count(),
        "avg_interview_score": round(response_stats["avg_score"] or 0),
        "recent_matches": recent_matches,
        "career_recommendations": career_recommendations,
        "ai_enabled": bool(__import__("django.conf", fromlist=["settings"]).settings.OPENAI_API_KEY),
    }
    return render(request, "dashboard/home.html", context)


def _build_career_recommendations(skills: set[str], latest_resume) -> list[dict]:
    target = (latest_resume.target_role if latest_resume else "") or "your target role"
    skill_list = sorted(skills)[:6]

    recommendations = [
        {
            "title": "Strengthen ATS alignment",
            "detail": f"Tailor keywords in your resume for {target}.",
        },
        {
            "title": "Close skill gaps",
            "detail": "Focus on missing skills from your latest job match results.",
        },
        {
            "title": "Practice mock interviews",
            "detail": "Complete at least one behavioral and one technical mock session weekly.",
        },
    ]

    if skill_list:
        recommendations.append(
            {
                "title": "Recommended learning path",
                "detail": f"Deepen: {', '.join(skill_list[:3])}.",
            }
        )
    else:
        recommendations.append(
            {
                "title": "Upload your resume",
                "detail": "Upload a resume to unlock personalized skill and course suggestions.",
            }
        )

    return recommendations
