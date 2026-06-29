from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AnswerForm, InterviewSetupForm
from .models import InterviewQuestion, InterviewResponse, InterviewSession
from .services.interview_ai import evaluate_response, generate_questions


@login_required
def session_list(request):
    sessions = InterviewSession.objects.filter(user=request.user)
    return render(request, "interviews/list.html", {"sessions": sessions})


@login_required
def session_create(request):
    if request.method == "POST":
        form = InterviewSetupForm(request.user, request.POST)
        if form.is_valid():
            resume = form.cleaned_data.get("resume")
            resume_text = resume.extracted_text if resume else ""
            target_role = form.cleaned_data["target_role"]
            difficulty = form.cleaned_data["difficulty"]

            question_sets = generate_questions(target_role, resume_text, difficulty)

            with transaction.atomic():
                session = InterviewSession.objects.create(
                    user=request.user,
                    resume=resume,
                    target_role=target_role,
                    difficulty=difficulty,
                )
                order = 1
                for question_type, questions in question_sets.items():
                    for text in questions:
                        InterviewQuestion.objects.create(
                            session=session,
                            question_type=question_type,
                            question_text=text,
                            order=order,
                        )
                        order += 1

            messages.success(request, "Interview session created.")
            return redirect("interviews:session_detail", pk=session.pk)
    else:
        form = InterviewSetupForm(request.user)

    return render(request, "interviews/create.html", {"form": form})


@login_required
def session_detail(request, pk):
    session = get_object_or_404(InterviewSession, pk=pk, user=request.user)
    questions = session.questions.select_related("response")
    return render(request, "interviews/detail.html", {"session": session, "questions": questions})


@login_required
def answer_question(request, pk):
    question = get_object_or_404(
        InterviewQuestion,
        pk=pk,
        session__user=request.user,
    )

    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            evaluation = evaluate_response(
                question.question_text,
                form.cleaned_data["answer_text"],
                question.session.target_role,
            )
            InterviewResponse.objects.update_or_create(
                question=question,
                defaults={
                    "answer_text": form.cleaned_data["answer_text"],
                    "confidence_score": evaluation.get("confidence_score", 0),
                    "relevance_score": evaluation.get("relevance_score", 0),
                    "completeness_score": evaluation.get("completeness_score", 0),
                    "overall_score": evaluation.get("overall_score", 0),
                    "feedback": evaluation.get("feedback", ""),
                    "suggestions": evaluation.get("suggestions", []),
                },
            )
            messages.success(request, "Answer submitted and evaluated.")
            return redirect("interviews:session_detail", pk=question.session_id)
    else:
        existing = getattr(question, "response", None)
        form = AnswerForm(initial={"answer_text": existing.answer_text if existing else ""})

    return render(
        request,
        "interviews/answer.html",
        {"question": question, "form": form, "response": getattr(question, "response", None)},
    )
