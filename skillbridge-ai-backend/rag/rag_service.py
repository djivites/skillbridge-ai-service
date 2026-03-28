import os
import json
import chromadb
from typing import Dict, Any, Optional

# Persistent client stores data on disk automatically, surviving restarts
CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "chroma_data")
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

# Using a standard collection for skills
skills_collection = client.get_or_create_collection(name="skills_resources")

def check_skill_exists(skill: str) -> bool:
    """Check if a skill's resources are already cached in Chroma."""
    result = skills_collection.get(ids=[skill])
    return len(result["ids"]) > 0

def check_skill_is_fully_cached(skill: str) -> bool:
    """Check if a skill's resources AND LLM precomputations are cached in Chroma."""
    result = skills_collection.get(ids=[skill])
    if result["ids"] and result["metadatas"] and len(result["metadatas"]) > 0:
        metadata = result["metadatas"][0]
        if metadata and "resources" in metadata:
            try:
                data = json.loads(metadata["resources"])
                if "precomputed_summary" in data and "precomputed_roadmap" in data:
                    return True
            except Exception:
                pass
    return False

def store_skill_resources(skill: str, data: Dict[str, Any]):
    """Store fetched resources for a skill into Chroma."""
    # We serialize the resources dictionary into a JSON string to store in metadata
    metadata = {"resources": json.dumps(data)}
    
    # Upsert to avoid duplication
    skills_collection.upsert(
        ids=[skill],
        documents=[skill],  # Add the skill name as the document for potential semantic search later
        metadatas=[metadata]
    )

def get_skill_resources(skill: str) -> Optional[Dict[str, Any]]:
    """Retrieve the stored resources for a skill from Chroma."""
    result = skills_collection.get(ids=[skill])
    if result["ids"] and result["metadatas"] and len(result["metadatas"]) > 0:
        metadata = result["metadatas"][0]
        # Return parsed JSON directly
        if metadata and "resources" in metadata:
            return json.loads(metadata["resources"])
    return None
