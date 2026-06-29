from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import JobMatchForm, ResumeUploadForm
from .models import JobMatch, Resume, ResumeAnalysis
from .services.analyzer import analyze_resume, match_job_description
from .services.parser import extract_text_from_file


@login_required
def resume_list(request):
    resumes = Resume.objects.filter(user=request.user)
    return render(request, "resumes/list.html", {"resumes": resumes})


@login_required
def resume_upload(request):
    if request.method == "POST":
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            resume.extracted_text = extract_text_from_file(resume.file.path)
            resume.save(update_fields=["extracted_text"])

            analysis_data = analyze_resume(resume.extracted_text, resume.target_role)
            ResumeAnalysis.objects.update_or_create(
                resume=resume,
                defaults={
                    "quality_score": analysis_data.get("quality_score", 0),
                    "ats_score": analysis_data.get("ats_score", 0),
                    "summary": analysis_data.get("summary", ""),
                    "strengths": analysis_data.get("strengths", []),
                    "improvements": analysis_data.get("improvements", []),
                    "keyword_suggestions": analysis_data.get("keyword_suggestions", []),
                    "grammar_notes": analysis_data.get("grammar_notes", []),
                    "skills": analysis_data.get("skills", []),
                    "sections": analysis_data.get("sections", {}),
                    "raw_response": analysis_data,
                },
            )
            messages.success(request, "Resume uploaded and analyzed successfully.")
            return redirect("resumes:detail", pk=resume.pk)
    else:
        form = ResumeUploadForm()

    return render(request, "resumes/upload.html", {"form": form})


@login_required
def resume_detail(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    analysis = getattr(resume, "analysis", None)
    job_matches = resume.job_matches.all()[:5]
    return render(
        request,
        "resumes/detail.html",
        {"resume": resume, "analysis": analysis, "job_matches": job_matches},
    )


@login_required
def job_match(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    result = None

    if request.method == "POST":
        form = JobMatchForm(request.POST)
        if form.is_valid():
            data = match_job_description(
                resume.extracted_text,
                form.cleaned_data["job_description"],
                form.cleaned_data["job_title"],
            )
            result = JobMatch.objects.create(
                resume=resume,
                job_title=form.cleaned_data["job_title"],
                job_description=form.cleaned_data["job_description"],
                compatibility_score=data.get("compatibility_score", 0),
                matched_skills=data.get("matched_skills", []),
                missing_skills=data.get("missing_skills", []),
                recommendations=data.get("recommendations", []),
                summary=data.get("summary", ""),
            )
            messages.success(request, "Job match analysis completed.")
    else:
        form = JobMatchForm(initial={"job_title": resume.target_role})

    return render(
        request,
        "resumes/job_match.html",
        {"resume": resume, "form": form, "result": result},
    )
