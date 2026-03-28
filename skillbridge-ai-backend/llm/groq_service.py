import json
import time
from typing import Dict, Any, List
from llm.groq_client import get_groq_client, get_groq_model

def call_groq_with_retry(prompt: str, json_mode: bool = False) -> str:
    """Helper function to execute Groq requests with a generic quota backoff."""
    client = get_groq_client()
    max_retries = 3
    for attempt in range(max_retries):
        try:
            kwargs = {
                "model": get_groq_model(),
                "messages": [{"role": "user", "content": prompt}]
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
                
            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message.content.strip()
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate limit" in error_str.lower():
                if attempt == max_retries - 1:
                    print(f"❌ Groq Rate Limit unresolved after {max_retries} retries: {error_str}")
                    raise e
                wait_time = 5 * (attempt + 1)
                print(f"⚠️ Groq Quota exceeded. Waiting {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(wait_time)
            else:
                # Re-raise other exceptions
                raise e
    return ""

def generate_summary(skill: str, wikipedia_text: str) -> str:
    """Generate a short summary using Groq API."""
    text = str(wikipedia_text)[:6000] if wikipedia_text else ""
    
    if text.startswith("{") and "'error'" in text:
        text = ""

    prompt = f"""
    You are an expert technical editor.
    Please write a simple, clean, and concise explanation of the technical skill '{skill}'. 
    Limit your explanation to a maximum of 150 words.
    """
    
    if text:
        prompt += f"\nHere is some exact Wikipedia reference information you can use:\n{text}\n"
    
    print(f"\n===== PROMPT TO SUMMARY MODEL (GROQ) =====\n{prompt}\n============================================\n")
    try:
        return call_groq_with_retry(prompt, json_mode=False)
    except Exception as e:
        print(f"Groq API error (Summary): {e}")
        return "Could not generate a specialized summary due to an API error."

def generate_roadmap(summary: str, github_data: List[Dict[str, Any]]) -> List[str]:
    """Generate a learning roadmap using Groq API."""
    prompt = f"""
You are an expert career and learning path advisor.
Based on the following summary and GitHub Roadmap data, create a focused, step-by-step roadmap to learn this skill.
Provide ONLY a valid JSON object with a single key "roadmap" containing an array of strings. Do not add any extra text or markdown formatting.

Example format:
{{
  "roadmap": [
    "Learn the core basics and syntax",
    "Build a basic Hello World project",
    "Explore core modules and standard libraries"
  ]
}}

Summary: {summary}
GitHub Roadmaps: {json.dumps(github_data[:3], indent=2)}
"""
    print(f"\n===== PROMPT TO ROADMAP MODEL (GROQ) =====\n{prompt}\n============================================\n")
    try:
        res_text = call_groq_with_retry(prompt, json_mode=True)
        # Parse JSON directly since Groq uses native JSON output avoiding markdown
        result = json.loads(res_text)
        if isinstance(result, dict) and "roadmap" in result:
            return [str(s) for s in result["roadmap"]]
        return ["Follow basic tutorials", "Practice building projects"]
    except Exception as e:
        print(f"Error generating roadmap with Groq: {e}")
        return ["Learn the basics", "Build a project"]

def estimate_time(roadmap: List[str], video_hours: float, hours_per_day: float) -> dict:
    """Estimate time to complete a roadmap using Groq API."""
    prompt = f"""
You are an expert learning planner.
I have a step-by-step roadmap for a skill. The total video tutorial duration I have found is {video_hours:.2f} hours.
I can study for {hours_per_day} hours per day.

Roadmap steps:
{json.dumps(roadmap, indent=2)}

Estimate the time required for EACH step. Return ONLY a valid JSON object matching this schema exactly. Ensure the `total_days` is a float, and `step_time_days` is an array of floats that matches the number of steps exactly. Do not wrap in markdown or add any extra text.

{{
  "step_time_days": [0.5, 1.2, 0.3],
  "total_days": 2.0
}}
"""
    print(f"\n===== PROMPT TO TIME ESTIMATOR MODEL (GROQ) =====\n{prompt}\n===================================================\n")
    try:
        res_text = call_groq_with_retry(prompt, json_mode=True)
        res = json.loads(res_text)
        
        step_time_days = res.get("step_time_days", [])
        total_days = res.get("total_days", 0.0)
        
        # Ensure array lengths match
        if len(step_time_days) != len(roadmap):
            default_days = video_hours / hours_per_day if hours_per_day > 0 else 0.0
            step_len = len(roadmap)
            step_time_days = [round(default_days/step_len, 2)] * step_len if step_len > 0 else []
            total_days = round(default_days, 2)
            
        return {
            "step_time_days": step_time_days,
            "total_days": round(total_days, 2)
        }
    except Exception as e:
        print(f"Error estimating time with Groq: {e}")
        default_days = video_hours / hours_per_day if hours_per_day > 0 else 0.0
        step_len = len(roadmap)
        return {
            "step_time_days": [round(default_days/step_len, 2)] * step_len if step_len > 0 else [],
            "total_days": round(default_days, 2)
        }
