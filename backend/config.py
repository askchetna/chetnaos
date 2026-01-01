import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class Settings:
    def __init__(self):
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        if not self.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY missing. Create a .env file or set the env var.")
        
        self.GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

def get_settings() -> Settings:
    """Get application settings with environment validation"""
    return Settings()
