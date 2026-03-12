import json
import logging
import os

import requests
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _ollama_base_url():
    return (
        os.getenv("OLLAMA_BASE_URL")
        or getattr(settings, "OLLAMA_BASE_URL", None)
        or "http://localhost:11434"
    ).rstrip("/")


def _ollama_lead_model():
    return (
        os.getenv("OLLAMA_LEAD_MODEL")
        or os.getenv("OLLAMA_MODEL")
        or getattr(settings, "OLLAMA_LEAD_MODEL", None)
        or "mistral-nemo:12b"
    )


def _ollama_timeout():
    raw_timeout = os.getenv("OLLAMA_TIMEOUT") or str(
        getattr(settings, "OLLAMA_TIMEOUT", 120)
    )
    try:
        return int(raw_timeout)
    except ValueError:
        return 120


def _chat_with_ollama(messages, json_mode=False, temperature=0.7):
    payload = {
        "model": _ollama_lead_model(),
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature},
    }
    if json_mode:
        payload["format"] = "json"

    response = requests.post(
        f"{_ollama_base_url()}/api/chat",
        json=payload,
        timeout=_ollama_timeout(),
    )
    response.raise_for_status()

    content = (response.json().get("message") or {}).get("content", "").strip()
    if not content:
        raise RuntimeError("Ollama returned an empty response")
    return content


def analyze_lead(inquiry_instance):
    """
    Sends inquiry data to a local Ollama model for lead analysis,
    then updates the instance with score, summary and email draft.
    """

    system_prompt = """
    You are 'Miss Bott', a premium technical consultant specializing in custom React, Django, and Headless Commerce architectures.
    
    Task 1: Evaluate the lead (Score 1-10).
    Task 2: Write a HYPER-PERSONALIZED email draft to the client.
    Task 3: Identify any red flags.
    
    Scoring Criteria (1-10):
    - 8-10 (Ideal): Budget > €6,000, specifically asks for React/Django/API work, clearly defined business goal (B2B/SaaS/E-commerce).
    - 5-7 (Maybe): Budget unclear but project sounds complex/interesting. Good technical literacy.
    - 1-4 (Avoid): Budget < €3,000, asking for Wordpress/Wix, vague "I need a website" requests, poor spelling/effort.

    Email Draft Instructions:
    - Tone: Professional, authoritative, yet warm.
    - If Score > 6: Write an invitation. Reference their SPECIFIC project details (e.g., "I saw you are migrating a FinTech app..."). Prove you read it.
    - If Score < 6: Write a polite decline (fully booked).
    - Do NOT include the Calendly link or sign-off (The system adds these). Just the body.

    Return strict JSON with this schema:
    {
      "summary": "Executive summary...",
      "score": integer,
      "red_flags": [],
      "recommended_action": "APPROVE" or "REJECT",
      "email_draft": "Hi [Name], \\n\\n[Body text here referencing their specific project needs...]"
    }
    """

    user_message = f"""
Analyze this lead:
Name: {inquiry_instance.name}
Email: {inquiry_instance.email}
Company: {inquiry_instance.company}
Budget: {inquiry_instance.get_budget_range_display()}
Timeline: {inquiry_instance.get_timeline_display()}
Service Interest: {inquiry_instance.service.name if inquiry_instance.service else 'General'}
Project Details: {inquiry_instance.project_details}
    """.strip()

    try:
        raw_content = _chat_with_ollama(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            json_mode=True,
            temperature=0.5,
        )
        data = json.loads(raw_content)

        score_raw = data.get("score", 0)
        try:
            score = int(score_raw)
        except (TypeError, ValueError):
            score = 0
        score = max(0, min(score, 10))

        inquiry_instance.ai_summary = data.get("summary", "")
        inquiry_instance.lead_score = score
        inquiry_instance.ai_email_draft = data.get("email_draft", "")

        flags = data.get("red_flags", [])
        action = data.get("recommended_action", "MANUAL_REVIEW")
        if not isinstance(flags, list):
            flags = [str(flags)]

        inquiry_instance.ai_analysis_raw = f"Action: {action}\nFlags: {', '.join(map(str, flags))}"
        inquiry_instance.status = "analyzed"
        inquiry_instance.is_analyzed = True

        inquiry_instance.save(
            update_fields=[
                "ai_summary",
                "lead_score",
                "ai_email_draft",
                "ai_analysis_raw",
                "status",
                "is_analyzed",
            ]
        )
        return True

    except Exception as exc:
        logger.error("AI analysis failed via Ollama: %s", exc)
        return False
