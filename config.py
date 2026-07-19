import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve and load .env file from the root directory
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

def get_api_key() -> str:
    """
    Safely retrieves the Gemini API key from environment variables.
    Raises ValueError if the key is missing.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not defined in environment variables or the local .env file. "
            "Please configure GEMINI_API_KEY in your .env file."
        )
    return api_key
