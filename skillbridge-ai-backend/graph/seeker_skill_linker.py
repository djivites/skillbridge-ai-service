from graph.neo4j_client import Neo4jClient

class SeekerSkillLinker:
    def __init__(self):
        self.db = Neo4jClient()

    def add_seeker(self, seeker_id: str):
        with self.db.driver.session() as s:
            s.run(
                "MERGE (:Seeker {id: $id})",
                id=seeker_id
            )

    def link_skill(self, seeker_id: str, skill: str):
        with self.db.driver.session() as s:
            s.run("""
                MATCH (s:Seeker {id: $sid})
                MATCH (k:Skill {name: $skill})
                MERGE (s)-[:KNOWS]->(k)
            """, sid=seeker_id, skill=skill)

    def link_skills(self, seeker_id: str, skills: set[str]):
        self.add_seeker(seeker_id)
        for skill in skills:
            self.link_skill(seeker_id, skill)
