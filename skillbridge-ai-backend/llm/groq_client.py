import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# We initialize the client once to be reused across extraction tools
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def get_groq_client():
    """Return the instantiated Groq client."""
    return client

def get_groq_model():
    """Return the default Groq model for fast JSON parsing operations."""
    return "llama-3.1-8b-instant"
