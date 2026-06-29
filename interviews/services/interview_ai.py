from core.ai_service import AIService


DEFAULT_QUESTIONS = {
    "technical": [
        "Explain a challenging technical problem you solved recently.",
        "How do you approach debugging production issues?",
        "Describe your experience with the core tools for this role.",
    ],
    "behavioral": [
        "Tell me about a time you handled conflict within a team.",
        "Describe a situation where you had to learn something quickly.",
        "Share an example of delivering results under a tight deadline.",
    ],
    "hr": [
        "Why are you interested in this role and company?",
        "Where do you see yourself in three years?",
        "What are your salary expectations and notice period?",
    ],
}


def generate_questions(target_role: str, resume_text: str, difficulty: str) -> dict[str, list[str]]:
    ai = AIService()
    if ai.available:
        result = ai.chat_json(
            system_prompt=(
                "Generate interview questions. Return JSON with keys technical, behavioral, hr "
                "each containing an array of 3 concise questions tailored to the candidate."
            ),
            user_prompt=(
                f"Role: {target_role}\nDifficulty: {difficulty}\n"
                f"Resume excerpt:\n{resume_text[:6000]}"
            ),
        )
        if result:
            return {
                "technical": result.get("technical", [])[:3],
                "behavioral": result.get("behavioral", [])[:3],
                "hr": result.get("hr", [])[:3],
            }

    prefix = {"easy": "Beginner", "medium": "Intermediate", "hard": "Advanced"}.get(difficulty, "")
    return {
        key: [f"[{prefix}] {question.replace('this role', target_role)}" for question in values]
        for key, values in DEFAULT_QUESTIONS.items()
    }


def evaluate_response(question: str, answer: str, target_role: str) -> dict:
    ai = AIService()
    if ai.available:
        result = ai.chat_json(
            system_prompt=(
                "Evaluate an interview answer. Return JSON with keys confidence_score, "
                "relevance_score, completeness_score, overall_score (0-100 each), "
                "feedback (string), suggestions (array of strings)."
            ),
            user_prompt=f"Role: {target_role}\nQuestion: {question}\nAnswer: {answer}",
        )
        if result:
            return result

    word_count = len(answer.split())
    completeness = min(100, 30 + word_count * 2)
    relevance = 70 if word_count > 20 else 45
    confidence = 65 if word_count > 15 else 40
    overall = round((completeness + relevance + confidence) / 3)

    return {
        "confidence_score": confidence,
        "relevance_score": relevance,
        "completeness_score": completeness,
        "overall_score": overall,
        "feedback": (
            "Heuristic feedback: expand your answer with a clear situation, action, and result."
        ),
        "suggestions": [
            "Use the STAR method (Situation, Task, Action, Result).",
            "Mention measurable outcomes where possible.",
            "Connect your answer directly to the target role requirements.",
        ],
    }
