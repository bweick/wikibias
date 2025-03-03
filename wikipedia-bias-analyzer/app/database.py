from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Create a database URL - psycopg3 requires postgresql+psycopg:// instead of postgresql://
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Create an engine instance with proper psycopg3 configuration
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    # These options help with psycopg3 integration
    future=True,
    pool_pre_ping=True,
)

# Create a SessionLocal class
# Each instance of SessionLocal will be a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class
# Models will inherit from this class
Base = declarative_base() 
