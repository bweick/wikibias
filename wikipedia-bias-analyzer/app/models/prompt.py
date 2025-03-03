from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, func
from sqlalchemy.orm import relationship

from app.database import Base

class PromptTemplate(Base):
    __tablename__ = "prompt_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    prompt_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f"<PromptTemplate(id={self.id}, name='{self.name}')>" 
