import os
import google.generativeai as genai
import json

# Ensure GEMINI_API_KEY is set in the environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

async def estimate_effort(title: str, description: str, task_type: str) -> float:
    """
    Uses the Gemini LLM to estimate the effort (in hours) required for a given task.
    """
    if not GEMINI_API_KEY:
        # Fallback if no key is provided
        fallbacks = {"EXAM": 10.0, "PROJECT": 8.0, "HOMEWORK": 3.0, "READING": 1.5}
        return fallbacks.get(task_type, 2.0)
        
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are an AI designed to estimate the time in hours required for a student to complete an academic task.
    Task Title: {title}
    Description: {description or 'No description provided.'}
    Task Type: {task_type}
    
    Respond ONLY with a JSON object in this format: {{"effort_estimate_hrs": 2.5}}
    Provide your best realistic estimate. If there's not enough info, provide a default based on the task type (e.g., Reading=1.0, Exam=10.0, Homework=2.0).
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        # Clean up Markdown JSON blocks if present
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
        
        data = json.loads(text.strip())
        return float(data.get("effort_estimate_hrs", 1.0))
    except Exception as e:
        print(f"LLM estimation error: {e}")
        fallbacks = {"EXAM": 10.0, "PROJECT": 8.0, "HOMEWORK": 3.0, "READING": 1.5}
        return fallbacks.get(task_type, 2.0)
