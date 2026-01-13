"""
AI-powered job analysis using OpenRouter API.

Provides functions for analyzing job matches and navigation steps.
Uses OpenAI-compatible API to access various LLM models through OpenRouter.
"""

from openai import AsyncOpenAI
import json
from app.config import settings
from app.db.models import UserProfile

# OpenRouter API Configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Configure OpenRouter Client
_client = None


def get_client() -> AsyncOpenAI:
    """Get or create the OpenRouter client."""
    global _client
    if _client is None and settings.OPENROUTER_API_KEY:
        _client = AsyncOpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=settings.OPENROUTER_API_KEY,
            default_headers={
                "HTTP-Referer": "https://github.com/job-auto-applier",
                "X-Title": "Job Auto-Applier"
            }
        )
    return _client


async def analyze_job_match(job_text: str, user_profile: UserProfile) -> dict:
    """
    Analyzes the match between a job description and the user profile using OpenRouter.
    
    Args:
        job_text: The full text of the job description.
        user_profile: The user's profile containing resume and preferences.
    
    Returns:
        A dict with 'match_score' (0-100), 'reasoning', and 'missing_skills'.
    """
    client = get_client()
    if not client:
        return {"match_score": 0, "reasoning": "API Key missing", "missing_skills": []}

    prompt = f"""You are an expert technical recruiter. Analyze the following candidate profile and job description.

CANDIDATE PROFILE:
Name: {user_profile.name}
Resume/Skills: {user_profile.resume_text}
Preferences: {user_profile.preferences}

JOB DESCRIPTION:
{job_text[:10000]}

Evaluate the match score (0-100) based on:
1. Technical skills alignment.
2. Years of experience alignment.
3. Location/Remote preferences (if specified in job).

Respond ONLY with valid JSON in this exact format:
{{
    "match_score": <int>,
    "reasoning": "<short explanation>",
    "missing_skills": ["<skill1>", "<skill2>"]
}}"""

    try:
        response = await client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": "You are a JSON-only response bot. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=500
        )
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print(f"AI Error: {e}")
        return {"match_score": 0, "reasoning": f"Error: {str(e)}", "missing_skills": []}


async def analyze_navigation_step(page_state: str, user_preferences: str) -> dict:
    """
    Determines the next action to take on a web page to filter for jobs.
    
    Args:
        page_state: The accessibility snapshot or semantic HTML of the page.
        user_preferences: The user's job preferences (e.g., "Remote, Python").
    
    Returns:
        A dict with 'action', 'selector', and optional 'value' for typing.
    """
    client = get_client()
    if not client:
        return {"action": "stop", "selector": None, "value": None}

    prompt = f"""You are a browser automation agent. Your goal is to filter a career page for: {user_preferences}.

PAGE STATE (Accessibility Snapshot / Semantic HTML):
{page_state[:15000]}

Decide the NEXT ONE step.
Respond ONLY with valid JSON:
{{
    "action": "click" | "type" | "stop",
    "selector": "<css_selector>",
    "value": "<text_to_type_if_type_action>"
}}
If you see a list of jobs already filtered, return action "stop"."""

    try:
        response = await client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": "You are a JSON-only response bot. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=200
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Nav Error: {e}")
        return {"action": "stop"}


async def test_api_connection() -> tuple[bool, str]:
    """
    Test the OpenRouter API connection.
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    client = get_client()
    if not client:
        return False, "OPENROUTER_API_KEY not configured"
    
    try:
        response = await client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=[{"role": "user", "content": "Say OK"}],
            max_tokens=5
        )
        if response.choices[0].message.content:
            return True, f"Connected to {settings.OPENROUTER_MODEL}"
        return False, "Empty response"
    except Exception as e:
        return False, str(e)
