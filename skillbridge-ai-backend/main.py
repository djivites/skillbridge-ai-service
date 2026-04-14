import os
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel

from utils.logger import get_logger
from services.roadmap_service import generate_personalized_roadmap
from utils.pdf_loader import extract_text_from_pdf
from llm.resume_skill_extractor import extract_raw_skills
from llm.job_skill_extractor import extract_job_skills
from llm.skill_canonicalizer import canonicalize_skills
from graph.seeker_skill_linker import SeekerSkillLinker
from graph.job_skill_linker import JobSkillLinker
from graph.skill_graph_builder import SkillGraphBuilder
from graph.similarity import SimilarityService

logger = get_logger("main")

app = FastAPI(
    title="SkillBridge AI API",
    description="Matches users to jobs based on skill graphs",
    version="1.0.0"
)

# Initialize specific services globally to reuse DB connections across requests
similarity_service = SimilarityService()
seeker_linker = SeekerSkillLinker()
job_linker = JobSkillLinker()
graph_builder = SkillGraphBuilder()

class JobCreateRequest(BaseModel):
    job_id: str
    skills_text: str
    title: Optional[str] = "Untitled Job"

class RoadmapRequest(BaseModel):
    user_id: str
    job_id: str
    hours_per_day: float

@app.get("/health", tags=["System"])
async def health_check():
    """Check if the API and database connection are healthy."""
    try:
        # Verify Neo4j connection
        driver = similarity_service.db.driver
        if driver:
            return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
    
    return {"status": "unhealthy", "database": "disconnected"}

@app.post("/reset-db", tags=["System"])
async def reset_database():
    """
    Clears all nodes and relationships from the Neo4j graph.
    USE WITH CAUTION.
    """
    try:
        # We can use any client that has a db reference
        similarity_service.db.clear_database()
        return {"message": "Neo4j Database cleared successfully."}
    except Exception as e:
        logger.error(f"Failed to clear database: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-job", tags=["Jobs"])
async def create_job(request: JobCreateRequest):
    """
    Create a new job matching profile by parsing required skills from text.
    """
    if not request.job_id.strip() or not request.skills_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="job_id and skills_text cannot be empty."
        )
        
    logger.info(f"Creating job {request.job_id}...")
    
    try:
        # Step 1: Extract Skills
        raw_skills = extract_job_skills(request.skills_text)
        
        # Step 2: Normalize Skills
        clean_skills = set(canonicalize_skills(raw_skills))
        
        if not clean_skills:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="No valid skills extracted from the text."
            )
            
        # Step 3: Build Graph Prerequisites
        graph_builder.build(clean_skills)
        
        # Step 3 & 4: Link Job and Trigger RAG caching natively via JobSkillLinker
        job_linker.add_job(request.job_id, request.title)
        job_linker.link_skills(request.job_id, clean_skills)
        
        # Step 5: Build Response
        return {
            "message": "Job created successfully",
            "job_id": request.job_id,
            "skills": list(clean_skills)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create job {request.job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/jobs", tags=["Jobs"])
async def get_all_jobs():
    """
    Retrieve all jobs and their required skills.
    """
    try:
        jobs_dict = similarity_service.get_all_jobs_skills()
        jobs_list = [
            {"job_id": j_id, "skills": list(skills)}
            for j_id, skills in jobs_dict.items()
        ]
        return {"jobs": jobs_list}
    except Exception as e:
        logger.error(f"Failed to retrieve jobs: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/job/{job_id}", tags=["Jobs"])
async def get_job(job_id: str):
    """
    Retrieve specific job details and its required skills.
    """
    try:
        skills = similarity_service.get_job_skills(job_id)
        if not skills:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Job {job_id} not found or has no documented skills."
            )
        return {
            "job_id": job_id,
            "skills": list(skills)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve job {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/match-jobs", tags=["Matching"])
async def match_jobs(
    user_id: str = Form(...),
    file: UploadFile = File(...),
    threshold: float = Form(default=0.0)
):
    """
    Process a user's resume, build their skill graph, and rank matching jobs.
    """
    if not user_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id cannot be empty"
        )
        
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be a PDF"
        )

    logger.info(f"Received match request for user_id: {user_id}")
    
    # Needs to be saved temporarily to disk since pdf_loader expects a file path
    temp_pdf_path = ""
    try:
        # Step 1. Load Resume
        logger.info("Step 1: Saving uploaded PDF to temporary file...")
        fd, temp_pdf_path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        
        with open(temp_pdf_path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        logger.info("Step 1: Extracting text from PDF...")
        resume_text = extract_text_from_pdf(temp_pdf_path)
        
        if not resume_text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Could not extract any text from the provided PDF."
            )
            
        # Step 2. Extract Skills
        logger.info("Step 2: Extracting raw skills via LLM...")
        raw_skills = extract_raw_skills(resume_text)
        if not raw_skills:
            logger.warning(f"No skills extracted from resume for user {user_id}.")
            raw_skills = []

        # Step 3. Normalize Skills
        logger.info(f"Step 3: Canonicalizing {len(raw_skills)} raw skills...")
        clean_skills_list = canonicalize_skills(raw_skills)
        clean_skills_set = set(clean_skills_list)
        logger.info(f"Final normalized skills: {clean_skills_list}")

        # Step 4. Build Graph
        # Even if they have no skills, we should at least record the user node in SeekerSkillLinker.
        logger.info("Step 4: Building graph. Precomputing prerequisites and merging skills...")
        if clean_skills_set:
            graph_builder.build(clean_skills_set)
            
        logger.info(f"Step 4: Linking user ({user_id}) to skills in Neo4j...")
        seeker_linker.link_skills(user_id, clean_skills_set)

        # Step 5. Compute Similarity
        logger.info("Step 5: Computing similarity against all jobs in database...")
        matches = similarity_service.rank_jobs_for_user(user_id, threshold=threshold)

        # Step 6. Return Response
        logger.info(f"Successfully matched {len(matches)} jobs for user {user_id}")
        return {
            "user_id": user_id,
            "matches": matches
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing matching for {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the request: {str(e)}"
        )
    finally:
        # Ensure temporary file is always cleaned up
        if os.path.exists(temp_pdf_path):
            try:
                os.remove(temp_pdf_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary PDF file {temp_pdf_path}: {e}")

@app.post("/generate-roadmap", tags=["Matching"])
async def generate_roadmap_endpoint(request: RoadmapRequest):
    """
    Generate a personalized learning roadmap based on missing skills.
    """
    try:
        if request.hours_per_day <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="hours_per_day must be greater than 0"
            )
            
        result = generate_personalized_roadmap(
            user_id=request.user_id,
            job_id=request.job_id,
            hours_per_day=request.hours_per_day
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating roadmap for user {request.user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating roadmap: {str(e)}"
        )

@app.get("/match-candidates/{job_id}", tags=["Matching"])
async def match_candidates(job_id: str, threshold: float = 0.0):
    """
    Rank all available users for a specific job based on their skill graph.
    """
    try:
        matches = similarity_service.rank_users_for_job(job_id, threshold=threshold)
        return {
            "job_id": job_id,
            "matches": matches
        }
    except Exception as e:
        logger.error(f"Error processing candidate matching for job {job_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the request: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
