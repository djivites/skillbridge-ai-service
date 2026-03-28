import json
from llm.groq_client import get_groq_client, get_groq_model

PROMPT = """
You are an AI system that extracts REQUIRED technical skills from job descriptions.

Rules:
- Extract ONLY technical skills
- Include explicitly mentioned skills
- Include implied skills
- Do NOT include soft skills
- Do NOT include company names
- Output MUST be valid JSON
- No explanations
- Follow EXACT schema:

{
  "skills": ["Skill1", "Skill2", "Skill3"]
}
"""

def extract_job_skills(job_text: str) -> list[str]:
    client = get_groq_client()
    try:
        response = client.chat.completions.create(
            model=get_groq_model(),
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": f"Job description:\n{job_text}"}
            ],
            response_format={"type": "json_object"}
        )

        raw = response.choices[0].message.content
        print("🔍 Job skill raw output:\n", raw)

        data = json.loads(raw)
        return list(set(data.get("skills", [])))
    except Exception as e:
        print("❌ Groq Error pulling Job skills:", str(e))
        return []