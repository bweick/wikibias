from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from typing import List

from app.database import Base

class WikipediaPage(Base):
    __tablename__ = "wikipedia_pages"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    last_fetched = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    analyses = relationship("BiasAnalysis", back_populates="page", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WikipediaPage(id={self.id}, title='{self.title}')>" 
