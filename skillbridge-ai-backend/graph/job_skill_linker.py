from graph.neo4j_client import Neo4jClient
from rag.rag_service import check_skill_is_fully_cached, store_skill_resources
import sys
import os

# To safely import agents.skill_extractor when called from scripts or main api
try:
    from agents.skill_extractor import fetch_all
except ImportError:
    # Just in case module run paths are mixed up
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from agents.skill_extractor import fetch_all

class JobSkillLinker:
    def __init__(self):
        self.db = Neo4jClient()

    def add_job(self, job_id: str, title: str):
        with self.db.driver.session() as session:
            session.run(
                """
                MERGE (:Job {id: $id, title: $title})
                """,
                id=job_id,
                title=title
            )

    def link_skills(self, job_id: str, skills: set[str]):
        # RAG CACHING PIPELINE FOR REQUIRED SKILLS
        for skill in skills:
            if not check_skill_is_fully_cached(skill):
                print(f"🔄 Fetching RAG learning resources for new job skill: {skill}")
                data = fetch_all(skill)
                
                print(f"🔄 Pre-computing LLM Summary and Roadmap for {skill}...")
                try:
                    from llm.groq_service import generate_summary, generate_roadmap
                    
                    wikipedia_text = data.get("wikipedia", "")
                    if isinstance(wikipedia_text, dict) and "error" in wikipedia_text:
                        wikipedia_text = ""
                    
                    summary = generate_summary(skill, wikipedia_text)
                    
                    github_data = data.get("github", [])
                    if isinstance(github_data, dict) and "error" in github_data:
                        github_data = []
                        
                    roadmap = generate_roadmap(summary, github_data)
                    
                    # Validate output to prevent storing garbage
                    if "error" in summary.lower() or not roadmap:
                        raise Exception("LLM Generation failed or returned an empty roadmap array.")
                        
                    data["precomputed_summary"] = summary
                    data["precomputed_roadmap"] = roadmap
                    
                    store_skill_resources(skill, data)
                    print(f"✅ Successfully cached RAG & LLM data for '{skill}'.")
                except Exception as e:
                    print(f"❌ CUDA/LLM Error during precomputation for {skill}: {e}")
                    print(f"⚠️ Aborting RAG storage for '{skill}' to prevent caching corrupted data.")
            else:
                print(f"✅ RAG Resources for '{skill}' already cached.")

        with self.db.driver.session() as session:
            for skill in skills:
                session.run(
                    """
                    MERGE (j:Job {id: $jid})
                    MERGE (k:Skill {name: $skill})
                    MERGE (j)-[:REQUIRES]->(k)
                    """,
                    jid=job_id,
                    skill=skill
                )