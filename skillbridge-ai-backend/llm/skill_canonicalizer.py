import json
from llm.groq_client import get_groq_client, get_groq_model

PROMPT = """
You are a skill normalization system.

Given a list of skills, return a canonical, standardized version.

Rules:
- Merge duplicates and synonyms
- Use industry-standard names
- Remove overly generic terms (e.g. "Computer Science", "Web Development")
- Keep ONLY technical skills
- Do NOT add new skills
- Do NOT explain anything
- Do NOT use markdown or backticks
- Output MUST be valid JSON
- Output MUST follow EXACTLY this schema and nothing else:

{
  "skills": ["Skill1", "Skill2", "Skill3"]
}
"""

def canonicalize_skills(skills: list[str]) -> list[str]:
    if not skills:
        return []
        
    client = get_groq_client()
    try:
        response = client.chat.completions.create(
            model=get_groq_model(),
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": f"Input skills:\n{json.dumps(skills, indent=2)}"}
            ],
            response_format={"type": "json_object"}
        )

        raw = response.choices[0].message.content
        print("🔍 Canonicalization raw output:\n", raw)
        data = json.loads(raw)
        
        if "skills" not in data or not isinstance(data["skills"], list):
            raise ValueError(f"Invalid schema from canonicalizer:\n{data}")

        return sorted(set(
            s.strip()
            for s in data["skills"]
            if isinstance(s, str) and s.strip()
        ))
        
    except Exception as e:
        print(f"❌ Groq Canonicalization Error: {e}")
        return skills # fallback to sending back original

