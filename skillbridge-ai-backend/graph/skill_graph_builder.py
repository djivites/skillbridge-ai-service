from graph.neo4j_client import Neo4jClient
from llm.prerequisite_inferer import infer_prerequisites

MAX_DEPTH = 2


class SkillGraphBuilder:
    def __init__(self):
        self.db = Neo4jClient()
        self.prereq_cache = {}

    def add_skill(self, skill: str):
        with self.db.driver.session() as session:
            session.run(
                "MERGE (:Skill {name: $name})",
                name=skill
            )

    def add_edge(self, skill: str, prereq: str):
        with self.db.driver.session() as session:
            session.run(
                """
                MATCH (a:Skill {name: $skill})
                MATCH (b:Skill {name: $prereq})
                MERGE (a)-[:REQUIRES]->(b)
                """,
                skill=skill,
                prereq=prereq
            )

    # 🔥 KEY CHANGE: one call only
    def precompute_prerequisites(self, skills: set[str]):
        """
        Call Gemini ONCE to get prerequisites for all skills.
        """
        results = infer_prerequisites(list(skills))
        self.prereq_cache.update(results)

    def expand_skill(self, skill: str, depth=0, visited=None):
        if visited is None:
            visited = set()

        if skill in visited or depth > MAX_DEPTH:
            return

        visited.add(skill)
        self.add_skill(skill)

        prereqs = self.prereq_cache.get(skill, [])

        for prereq in prereqs:
            self.add_skill(prereq)
            self.add_edge(skill, prereq)
            self.expand_skill(prereq, depth + 1, visited)

    def build(self, skills: set[str]):
        # 🔥 Precompute ONCE
        self.precompute_prerequisites(skills)

        for skill in skills:
            self.expand_skill(skill)

