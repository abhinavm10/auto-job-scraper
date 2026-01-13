"""
AI-powered job analysis using Google's Gemini API.

Provides functions for analyzing job matches and navigation steps.
"""

import google.generativeai as genai
import json
from app.config import settings
from app.db.models import UserProfile

# Configure Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)


async def analyze_job_match(job_text: str, user_profile: UserProfile) -> dict:
    """
    Analyzes the match between a job description and the user profile using Gemini.
    
    Args:
        job_text: The full text of the job description.
        user_profile: The user's profile containing resume and preferences.
    
    Returns:
        A dict with 'match_score' (0-100), 'reasoning', and 'missing_skills'.
    """
    if not settings.GEMINI_API_KEY:
        return {"match_score": 0, "reasoning": "API Key missing", "missing_skills": []}

    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are an expert technical recruiter. Analyze the following candidate profile and job description.
    
    CANDIDATE PROFILE:
    Name: {user_profile.name}
    Resume/Skills: {user_profile.resume_text}
    Preferences: {user_profile.preferences}
    
    JOB DESCRIPTION:
    {job_text[:10000]} # Truncate if too long
    
    Evaluate the match score (0-100) based on:
    1. Technical skills alignment.
    2. Years of experience alignment.
    3. Location/Remote preferences (if specified in job).
    
    Provide a JSON response strictly in this format:
    {{
        "match_score": <int>,
        "reasoning": "<short explanation>",
        "missing_skills": ["<skill1>", "<skill2>"]
    }}
    """
    
    try:
        response = await model.generate_content_async(
            prompt, 
            generation_config={"response_mime_type": "application/json"}
        )
        result = json.loads(response.text)
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
    if not settings.GEMINI_API_KEY:
        return {"action": "stop", "selector": None, "value": None}

    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are a browser automation agent. Your goal is to filter a career page for: {user_preferences}.
    
    PAGE STATE (Accessibility Snapshot / Semantic HTML):
    {page_state[:15000]}
    
    Decide the NEXT ONE step.
    Return JSON:
    {{
        "action": "click" | "type" | "stop",
        "selector": "<css_selector>",
        "value": "<text_to_type_if_type_action>"
    }}
    If you see a list of jobs already filtered, return action "stop".
    """
    
    try:
        response = await model.generate_content_async(
            prompt, 
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Nav Error: {e}")
        return {"action": "stop"}
