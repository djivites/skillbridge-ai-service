from typing import List, Dict, Any, Optional
from graph.neo4j_client import Neo4jClient

class SimilarityService:
    """
    Service to compute similarity between users and jobs based on their skills.
    Supports Jaccard and Weighted Match Score (Primary).
    """
    def __init__(self):
        self.db = Neo4jClient()

    def get_user_skills(self, user_id: str) -> set[str]:
        """Fetch all skills for a given user."""
        # Attempt to use schema from prompt, falling back to older Seeker schema if empty
        query = """
        MATCH (u:User {user_id: $user_id})-[:HAS_SKILL]->(s:Skill)
        RETURN s.name AS skill
        """
        fallback_query = """
        MATCH (u:Seeker {id: $user_id})-[:KNOWS]->(s:Skill)
        RETURN s.name AS skill
        """
        with self.db.driver.session() as session:
            result = session.run(query, user_id=user_id)
            skills = {record["skill"] for record in result}
            
            if not skills:
                result = session.run(fallback_query, user_id=user_id)
                skills = {record["skill"] for record in result}
                
        return skills

    def get_job_skills(self, job_id: str) -> set[str]:
        """Fetch all required skills for a given job."""
        # Assume both id and job_id might be used based on codebase vs prompt inconsistencies
        query = """
        MATCH (j:Job)-[:REQUIRES]->(s:Skill)
        WHERE j.id = $job_id OR j.job_id = $job_id
        RETURN s.name AS skill
        """
        with self.db.driver.session() as session:
            result = session.run(query, job_id=job_id)
            skills = {record["skill"] for record in result}
                
        return skills

    def get_all_jobs_skills(self) -> Dict[str, set[str]]:
        """Fetch required skills for all jobs in a single batch query."""
        query = """
        MATCH (j:Job)
        OPTIONAL MATCH (j)-[:REQUIRES]->(s:Skill)
        RETURN coalesce(j.id, j.job_id) AS job_id, collect(s.name) AS skills
        """
        jobs: Dict[str, set[str]] = {}
        with self.db.driver.session() as session:
            result = session.run(query)
            for record in result:
                job_id = record["job_id"]
                if job_id:
                    # Filter out null values from OPTIONAL MATCH
                    skills_list = [s for s in record["skills"] if s is not None]
                    jobs[job_id] = set(skills_list)
        return jobs

    def get_all_users_skills(self) -> Dict[str, set[str]]:
        """Fetch skills for all users in a single batch query."""
        query = """
        MATCH (u:User)-[:HAS_SKILL]->(s:Skill)
        RETURN coalesce(u.id, u.user_id) AS user_id, collect(s.name) AS skills
        """
        fallback_query = """
        MATCH (u:Seeker)-[:KNOWS]->(s:Skill)
        RETURN u.id AS user_id, collect(s.name) AS skills
        """
        users: Dict[str, set[str]] = {}
        with self.db.driver.session() as session:
            result = session.run(query)
            for record in result:
                if record["user_id"]:
                    users[record["user_id"]] = set(record["skills"])
            
            if not users:  # Fallback to Seeker schema if no Users found
                result = session.run(fallback_query)
                for record in result:
                    if record["user_id"]:
                        users[record["user_id"]] = set(record["skills"])
        return users

    def compute_jaccard(self, user_skills: set[str], job_skills: set[str]) -> float:
        """Calculate Jaccard similarity."""
        if not user_skills and not job_skills:
            return 0.0
        intersection = user_skills.intersection(job_skills)
        union = user_skills.union(job_skills)
        return len(intersection) / len(union) if union else 0.0

    def compute_weighted_score(self, user_skills: set[str], job_skills: set[str]) -> float:
        """Calculate Weighted Match Score (PRIMARY METHOD)."""
        if not job_skills:
            return 1.0 if user_skills else 0.0
        matched = user_skills.intersection(job_skills)
        return len(matched) / len(job_skills)

    def compute_similarity(self, user_skills: set[str], job_skills: set[str]) -> Dict[str, Any]:
        """Compute match logic returning structured data (including gaps)."""
        # Removed RAG pre-fetch logic
        matched = list(user_skills.intersection(job_skills))
        missing = sorted(list(job_skills - user_skills))
        
        score = self.compute_weighted_score(user_skills, job_skills)
        
        return {
            "score": round(score, 4),
            "matched_skills": sorted(matched),
            "missing_skills": missing
        }

    def rank_jobs_for_user(self, user_id: str, threshold: float = 0.0) -> List[Dict[str, Any]]:
        """Rank jobs for a user based on similarity."""
        # Removed RAG pre-fetch logic
        user_skills = self.get_user_skills(user_id)
        if not user_skills:
            user_skills = set()

        query = """
        MATCH (j:Job)
        RETURN coalesce(j.id, j.job_id) AS job_id
        """
        all_jobs = []
        with self.db.driver.session() as session:
            result = session.run(query)
            for record in result:
                if record["job_id"]:
                    all_jobs.append(record["job_id"])

        print(f"Total jobs found: {len(all_jobs)}")

        if not all_jobs:
            return []
            
        results = []
        
        for job_id in all_jobs:
            print(f"Processing job: {job_id}")
            
            job_skills = self.get_job_skills(job_id)
            
            total_required_skills = len(job_skills)
            matched_skills_set = user_skills.intersection(job_skills)
            matched_required_skills = len(matched_skills_set)
            
            if total_required_skills > 0:
                score = matched_required_skills / total_required_skills
            else:
                score = 1.0 if user_skills else 0.0
                
            print(f"Score: {score}")

            matched_skills = sorted(list(matched_skills_set))
            missing_skills_list = sorted(list(job_skills - user_skills))

            missing_skills = missing_skills_list

            if threshold is not None:
                if score >= threshold:
                    results.append({
                        "job_id": job_id,
                        "score": round(score, 4),
                        "matched_skills": matched_skills,
                        "missing_skills": missing_skills
                    })
            else:
                results.append({
                    "job_id": job_id,
                    "score": round(score, 4),
                    "matched_skills": matched_skills,
                    "missing_skills": missing_skills
                })

        # Sort descending by score
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def rank_users_for_job(self, job_id: str, threshold: float = 0.0) -> List[Dict[str, Any]]:
        """Rank users for a job based on similarity."""
        job_skills = self.get_job_skills(job_id)
        if not job_skills:
            return []

        users_skills = self.get_all_users_skills()
        results = []
        
        for user_id, user_skills in users_skills.items():
            sim_data = self.compute_similarity(user_skills, job_skills)
            if sim_data["score"] >= threshold:
                results.append({
                    "user_id": user_id,
                    **sim_data
                })

        # Sort descending by score
        return sorted(results, key=lambda x: x["score"], reverse=True)
