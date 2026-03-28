import json
import re
from llm.groq_client import get_groq_client, get_groq_model

PROMPT = """
You are a deterministic technical prerequisite inference engine.

Your task:
For each given skill, list ONLY its essential, concrete prerequisite technical skills.

STRICT RULES:

1. Output MUST be valid JSON only.
2. Do NOT include the original skill as its own prerequisite.
3. Include ONLY direct, learnable technical prerequisites.
4. Use standardized, industry-recognized canonical skill names.
5. Normalize singular/plural forms:
   - Use plural when standard (e.g. "Operating Systems", "Database Systems").
6. Expand common abbreviations:
   - "OS" → "Operating Systems"
   - "DBMS" → "Database Systems"
   - "ML" → "Machine Learning"
   - "NLP" → "Natural Language Processing"
7. DO NOT include vague or abstract terms such as:
   - "Concepts"
   - "Fundamentals"
   - "Basics"
   - "Introduction"
   - "Computer Science"
   - "Software Development"
   - "Web Development"
8. Do NOT include soft skills.
9. Do NOT explain anything.
10. Do NOT add text before or after the JSON.

IMPORTANT:
- Prefer concrete prerequisite skills over abstract descriptions.
- If no real prerequisite exists, return an empty list for that skill.

OUTPUT FORMAT (EXACT JSON OBJECT NO MARKDOWN):

{
  "SkillA": ["Prerequisite1", "Prerequisite2"],
  "SkillB": []
}

"""

def infer_prerequisites(skills: list[str]) -> dict:
    if not skills:
        return {}
        
    client = get_groq_client()
    try:
        response = client.chat.completions.create(
            model=get_groq_model(),
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": f"Skills:\n{json.dumps(skills, indent=2)}"}
            ],
            response_format={"type": "json_object"}
        )

        raw = response.choices[0].message.content
        print("🔍 Prerequisite raw output:\n", raw)

        data = json.loads(raw)

        # Defensive cleaning
        cleaned = {}
        for skill, prereqs in data.items():
            if isinstance(prereqs, list):
                cleaned[skill] = [
                    p for p in prereqs
                    if isinstance(p, str) and p.strip() and p != skill
                ]
            else:
                cleaned[skill] = []

        return cleaned
    except Exception as e:
        print(f"❌ Groq Inference Error: {e}")
        return {s: [] for s in skills}

