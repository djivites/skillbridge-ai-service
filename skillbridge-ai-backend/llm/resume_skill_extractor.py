import json
from llm.groq_client import get_groq_client, get_groq_model

PROMPT = """
You are an AI system that extracts technical skills from resumes.

Rules:
- Extract ONLY technical / domain skills
- Include skills mentioned explicitly
- Include skills implied by experience or projects
  Examples:
  - Django implies Python
  - Sentiment Analysis implies NLP
- Do NOT include soft skills
- Do NOT include duplicates
- Do NOT explain anything
- Output MUST be valid JSON
- Output MUST NOT contain markdown, backticks, or commentary

Return ONLY valid JSON in this format:
{
  "skills": ["skill1", "skill2", "skill3"]
}
"""

def extract_raw_skills(resume_text: str) -> list[str]:
    client = get_groq_client()
    try:
        response = client.chat.completions.create(
            model=get_groq_model(),
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": f"RESUME TEXT:\n{resume_text}"}
            ],
            response_format={"type": "json_object"}
        )

        raw = response.choices[0].message.content
        print("🔍 Resume parsing raw output:\n", raw)

        data = json.loads(raw)
        skills = data.get("skills", [])
        return sorted(set(s.strip() for s in skills if s.strip()))
        
    except json.JSONDecodeError as e:
        print("❌ Groq returned INVALID JSON", str(e))
        return []
    except Exception as e:
        print("❌ Groq Error parsing Resume skills:", str(e))
        return []
