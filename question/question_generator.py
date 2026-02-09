"""
Question generator via OpenRouter API.
Supports MCQs, fill in the blanks, and short answers.
"""

import json
import re
from openai import OpenAI

from config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    DEFAULT_MODEL,
    MAX_TOKENS,
    TEMPERATURE,
)


def get_openrouter_client(api_key: str | None = None) -> OpenAI:
    """Crée un client OpenAI configuré pour OpenRouter."""
    key = (api_key or "").strip() or OPENROUTER_API_KEY
    return OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=key,
    )


QUESTION_TYPES = {
    "mcq": "MCQ (Multiple choice)",
    "fill_blank": "Fill in the blanks",
    "short_answer": "Short answer",
}

SYSTEM_PROMPTS = {
    "mcq": """You are an expert teacher. Generate multiple choice questions (MCQs) from the provided text.
IMPORTANT: Generate ALL questions and options in English only.
Output format: JSON only, no text before or after:
{
  "questions": [
    {
      "question": "The question here?",
      "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
      "correct": "A"
    }
  ]
}
Generate 5 MCQs. Indicate the correct answer in "correct" (A, B, C or D).""",

    "fill_blank": """You are an expert teacher. Generate fill-in-the-blank questions from the provided text.
IMPORTANT: Generate ALL sentences and answers in English only.
Use _____ to indicate the missing word(s) in each sentence.
Output format: JSON only, no text before or after:
{
  "questions": [
    {
      "sentence": "The sentence with _____ for the missing word.",
      "answer": "the missing word"
    }
  ]
}
Generate 5 fill-in-the-blank questions.""",

    "short_answer": """You are an expert teacher. Generate short answer questions from the provided text.
IMPORTANT: Generate ALL questions and expected answers in English only.
Output format: JSON only, no text before or after:
{
  "questions": [
    {
      "question": "The question here?",
      "expected_answer": "Expected answer (for grading)"
    }
  ]
}
Generate 5 short answer questions.""",
}


def _extract_json(content: str) -> dict | None:
    """Extract JSON from response, handling markdown code blocks."""
    content = content.strip()
    # Remove ```json or ``` wrapper
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
    if match:
        content = match.group(1).strip()
    # Try to find JSON object
    match = re.search(r"\{[\s\S]*\}", content)
    if match:
        content = match.group(0)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None


def generate_questions(
    pdf_text: str,
    question_type: str,
    model: str | None = None,
    api_key: str | None = None,
) -> tuple[list[dict], str | None]:
    """
    Generate questions from PDF text via OpenRouter.

    Returns:
        (questions_list, error_message)
        If successful: (questions, None)
        If failed: ([], "error description")
    """
    if not pdf_text or len(pdf_text.strip()) < 50:
        return [], "PDF text is too short (minimum 50 characters required)."

    model = model or DEFAULT_MODEL
    client = get_openrouter_client(api_key=api_key)
    system_prompt = SYSTEM_PROMPTS.get(
        question_type,
        SYSTEM_PROMPTS["mcq"]
    )

    max_chars = 8000
    text_chunk = pdf_text[:max_chars]
    if len(pdf_text) > max_chars:
        text_chunk += "\n\n[... text truncated ...]"

    user_content = f"""Here is the document content:

---
{text_chunk}
---

Generate "{QUESTION_TYPES[question_type]}" questions based on this content. All questions and answers must be in English."""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
    except Exception as e:
        err = str(e).strip()
        if "401" in err or "Incorrect API key" in err or "invalid_api_key" in err:
            return [], "Invalid API key. Check your OpenRouter key at https://openrouter.ai/keys"
        if "404" in err or "model" in err.lower():
            return [], f"Model not found. Try a different model (e.g. meta-llama/llama-3.2-3b-instruct:free). Original: {err[:200]}"
        if "429" in err or "rate" in err.lower():
            return [], "Rate limit exceeded. Wait a moment and try again, or use a different model."
        return [], f"API error: {err[:300]}"

    content = response.choices[0].message.content
    if not content:
        return [], "Model returned empty response. Try a different model."

    data = _extract_json(content)
    if not data:
        return [], f"Could not parse model response as JSON. Try again or a different model. Raw: {content[:200]}..."

    questions = data.get("questions", [])
    if not questions:
        return [], "Model returned no questions. Try again or a different model."
    return questions, None