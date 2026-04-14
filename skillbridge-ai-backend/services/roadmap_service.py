import json
import traceback
from graph.similarity import SimilarityService
from rag.rag_service import get_skill_resources
from typing import Dict, Any

from llm.groq_service import generate_summary, generate_roadmap, estimate_time

similarity_service = SimilarityService()

def parse_duration_to_hours(duration_str: str) -> float:
    """Parse output of str(datetime.timedelta) like '1:23:45' or '1 day, 2:00:00' to hours."""
    try:
        days = 0
        if 'day' in duration_str:
            parts = duration_str.split(',')
            days_str = parts[0].replace('days', '').replace('day', '').strip()
            days = float(days_str)
            time_str = parts[1].strip() if len(parts) > 1 else "0:0:0"
        else:
            time_str = duration_str.strip()
            
        time_parts = time_str.split(':')
        hours, minutes, seconds = 0, 0, 0
        if len(time_parts) == 3:
            hours, minutes, seconds = map(float, time_parts)
        elif len(time_parts) == 2:
            minutes, seconds = map(float, time_parts)
            
        return days * 24 + hours + minutes / 60 + seconds / 3600
    except Exception:
        return 0.1 # default 6 mins if parsing fails

def generate_personalized_roadmap(user_id: str, job_id: str, hours_per_day: float) -> Dict[str, Any]:
    # 1. Get missing skills
    user_skills = similarity_service.get_user_skills(user_id)
    job_skills = similarity_service.get_job_skills(job_id)
    
    missing_skills = sorted(list(job_skills - user_skills))
    
    if not missing_skills:
        return {
            "job_id": job_id,
            "skills": [],
            "overall_days": 0.0,
            "message": "You already have all the required skills for this job!"
        }
        
    skills_list = []
    overall_days = 0.0
    
    # 2. Process each missing skill
    for skill in missing_skills:
        # Fetch RAG data
        skill_data = get_skill_resources(skill) or {}
        
        # Youtube handling
        youtube_data = skill_data.get("youtube", [])
        if isinstance(youtube_data, dict) and "error" in youtube_data:
            youtube_data = []
            
        video_hours = 0.0
        youtube_url = None
        if youtube_data:
            first_video = youtube_data[0]
            dur_str = first_video.get("duration", "0:0:0")
            video_hours = parse_duration_to_hours(dur_str)
            youtube_url = first_video.get("url", None)
            
        # Github handling
        github_data = skill_data.get("github", [])
        if isinstance(github_data, dict) and "error" in github_data:
            github_data = []
            
        # Check cache for Pre-computed Summary & Roadmap
        summary = skill_data.get("precomputed_summary")
        roadmap_steps = skill_data.get("precomputed_roadmap")
        
        if not summary or not roadmap_steps:
            print(f"⚠️ Precomputed data missing in RAG for {skill}. Generating dynamically via LLM...")
            try:
                summary = generate_summary(skill)
                roadmap_steps = generate_roadmap(skill)
            except Exception as e:
                print(f"Failed to generate summary/roadmap for {skill}: {e}")
                summary = "Summary not available yet. The Job Provider has not fully generated this skill's roadmap."
                roadmap_steps = ["1. Learn the absolute basics", "2. Review documentation and core concepts", "3. Complete a portfolio project"]
        else:
            print(f"⚡ Loaded precomputed Summary & Roadmap instantly from cache for {skill}!")
        
        # Step 5: Ollama Time Estimation
        print(f"Estimating time for {skill}...")
        time_data = estimate_time(roadmap_steps, video_hours, hours_per_day)
        
        total_days = time_data.get("total_days", 0.0)
        overall_days += total_days
        
        skills_list.append({
            "skill": skill,
            "youtube_url": youtube_url,
            "summary": summary,
            "roadmap": roadmap_steps,
            "step_time_days": time_data.get("step_time_days", []),
            "total_days": round(total_days, 2)
        })
        
    return {
        "job_id": job_id,
        "skills": skills_list,
        "overall_days": round(overall_days, 2)
    }
