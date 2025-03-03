from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

class BiasAnalysis(Base):
    __tablename__ = "bias_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("wikipedia_pages.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="pending", nullable=False)  # pending, processing, completed, failed
    prompt_id = Column(Integer, ForeignKey("prompt_templates.id"), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    section_name = Column(String(255), nullable=True)  # Added for our tests
    analysis_result = Column(Text, nullable=True)      # Added for our tests
    score = Column(Integer, nullable=True)             # Optional bias score
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)  # Added for our tests
    
    # Relationships - maintain all original relationships
    page = relationship("WikipediaPage", back_populates="analyses")
    prompt = relationship("PromptTemplate")
    aggregated_results = relationship("AggregatedResult", back_populates="analysis", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<BiasAnalysis(id={self.id}, status='{self.status}')>"

class BiasResult(Base):
    __tablename__ = "bias_results"
    
    id = Column(Integer, primary_key=True, index=True)
    aggregated_result_id = Column(Integer, ForeignKey("aggregated_results.id"), nullable=False)
    section_name = Column(String(255), nullable=False)
    section_content = Column(Text, nullable=False)
    iteration = Column(Integer, nullable=False)
    raw_llm_response = Column(Text, nullable=False)
    processed_results = Column(Text, nullable=False)  # JSON string of extracted biases
    processing_timestamp = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    aggregated_result = relationship("AggregatedResult", back_populates="results")
    bias_instances = relationship("BiasInstance", back_populates="result", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<BiasResult(id={self.id}, section='{self.section_name}', iteration={self.iteration})>"

class BiasInstance(Base):
    __tablename__ = "bias_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey("bias_results.id"), nullable=False)
    bias_type = Column(String(50), nullable=False)
    rationale = Column(Text, nullable=False)
    affected_stakeholder = Column(String(255), nullable=True)
    biased_phrase = Column(Text, nullable=False)
    start_index = Column(Integer, nullable=True)  # Position in the text where bias starts
    end_index = Column(Integer, nullable=True)    # Position in the text where bias ends
    
    # Relationships
    result = relationship("BiasResult", back_populates="bias_instances")
    
    def __repr__(self):
        return f"<BiasInstance(id={self.id}, bias_type='{self.bias_type}')>"

class AggregatedResult(Base):
    __tablename__ = "aggregated_results"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("bias_analyses.id"), nullable=False)
    section_name = Column(String(255), nullable=False)
    biased_phrases = Column(JSON, nullable=False)  # JSON with phrase and count
    heatmap_data = Column(JSON, nullable=False)    # JSON with heatmap entries
    result_metadata = Column(JSON, nullable=True)  # Additional metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    analysis = relationship("BiasAnalysis", back_populates="aggregated_results")
    results = relationship("BiasResult", back_populates="aggregated_result", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AggregatedResult(id={self.id}, section='{self.section_name}')>" 
