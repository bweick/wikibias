from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Wikipedia Bias Analyzer"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database settings
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/wikipedia_bias"
    
    # Authentication settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-development-only")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]  # Update for production

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings() 
