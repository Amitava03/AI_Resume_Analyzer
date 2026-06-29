import json
import os
import re
from typing import Any

from django.conf import settings


class AIService:
    """OpenAI wrapper with heuristic fallback when no API key is configured."""

    def __init__(self) -> None:
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self._client = None

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    @property
    def client(self):
        if self._client is None and self.available:
            from openai import OpenAI

            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def chat_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        if not self.available:
            return {}

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)

    def chat_text(self, system_prompt: str, user_prompt: str) -> str:
        if not self.available:
            return ""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
        )
        return response.choices[0].message.content or ""


def extract_keywords(text: str, limit: int = 30) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z+#.]{1,}", text.lower())
    stopwords = {
        "the", "and", "for", "with", "that", "this", "from", "your", "have",
        "will", "are", "you", "our", "job", "role", "work", "team", "using",
        "experience", "skills", "ability", "required", "preferred",
    }
    freq: dict[str, int] = {}
    for word in words:
        if len(word) < 3 or word in stopwords:
            continue
        freq[word] = freq.get(word, 0) + 1
    ranked = sorted(freq.items(), key=lambda item: item[1], reverse=True)
    return [word for word, _ in ranked[:limit]]


def keyword_overlap_score(resume_text: str, job_text: str) -> tuple[int, list[str], list[str]]:
    resume_keywords = set(extract_keywords(resume_text))
    job_keywords = set(extract_keywords(job_text))
    if not job_keywords:
        return 0, [], []
    matched = sorted(resume_keywords & job_keywords)
    missing = sorted(job_keywords - resume_keywords)
    score = round((len(matched) / len(job_keywords)) * 100)
    return score, matched, missing
