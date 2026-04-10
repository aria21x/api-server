# At the very end of core/config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Dynamic settings loader for Railway compatibility"""
    def __getattr__(self, name):
        return os.getenv(name)
    
    def get(self, name, default=None):
        return os.getenv(name, default)

settings = Settings()
