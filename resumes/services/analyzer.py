from core.ai_service import AIService, extract_keywords, keyword_overlap_score
from resumes.services.parser import extract_skills, parse_sections


def analyze_resume(text: str, target_role: str = "") -> dict:
    sections = parse_sections(text)
    skills = extract_skills(text)
    word_count = len(text.split())
    ai = AIService()

    if ai.available:
        result = ai.chat_json(
            system_prompt=(
                "You are an expert resume coach and ATS specialist. "
                "Return JSON with keys: quality_score (0-100), ats_score (0-100), "
                "summary, strengths (array), improvements (array), "
                "keyword_suggestions (array), grammar_notes (array)."
            ),
            user_prompt=(
                f"Target role: {target_role or 'General'}\n\nResume:\n{text[:12000]}"
            ),
        )
        if result:
            result["skills"] = skills
            result["sections"] = sections
            return result

    ats_score, matched, missing = keyword_overlap_score(text, target_role or text)
    quality_score = min(100, 45 + min(word_count // 10, 25) + len(skills) * 3)

    return {
        "quality_score": quality_score,
        "ats_score": max(ats_score, min(85, 40 + len(skills) * 4)),
        "summary": (
            "Heuristic analysis completed. Add OPENAI_API_KEY for deeper AI insights."
        ),
        "strengths": skills[:5] or ["Resume uploaded and parsed successfully."],
        "improvements": [
            "Quantify achievements with metrics where possible.",
            "Align skills section with your target job description.",
            "Use clear section headings for ATS parsing.",
        ],
        "keyword_suggestions": missing[:8] or extract_keywords(target_role or text, 8),
        "grammar_notes": [
            "Use consistent tense for current vs past roles.",
            "Keep bullet points concise and action-oriented.",
        ],
        "skills": skills,
        "sections": sections,
        "matched_keywords": matched,
        "missing_keywords": missing,
    }


def match_job_description(resume_text: str, job_description: str, job_title: str = "") -> dict:
    ai = AIService()
    base_score, matched, missing = keyword_overlap_score(resume_text, job_description)

    if ai.available:
        result = ai.chat_json(
            system_prompt=(
                "You are a hiring analyst. Return JSON with keys: "
                "compatibility_score (0-100), summary, matched_skills (array), "
                "missing_skills (array), recommendations (array)."
            ),
            user_prompt=(
                f"Job title: {job_title}\n\nJob description:\n{job_description[:8000]}\n\n"
                f"Resume:\n{resume_text[:8000]}"
            ),
        )
        if result:
            result.setdefault("compatibility_score", base_score)
            return result

    return {
        "compatibility_score": base_score,
        "summary": "Keyword-based compatibility estimate (configure OpenAI for richer matching).",
        "matched_skills": matched,
        "missing_skills": missing,
        "recommendations": [
            "Mirror important keywords from the job description naturally in your resume.",
            "Add projects or experience that demonstrate missing skills.",
            "Tailor your professional summary to the target role.",
        ],
    }
