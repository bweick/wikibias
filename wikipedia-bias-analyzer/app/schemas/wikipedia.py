from pydantic import BaseModel, HttpUrl, Field
from typing import Dict, Optional
from datetime import datetime

class WikipediaUrlRequest(BaseModel):
    """Schema for a Wikipedia URL request."""
    url: HttpUrl = Field(..., description="URL of the Wikipedia page to process")

class WikipediaPageResponse(BaseModel):
    """Schema for a Wikipedia page response."""
    id: int
    url: str
    title: str
    last_fetched: datetime
    
    class Config:
        from_attributes = True

class WikipediaPageDetailResponse(WikipediaPageResponse):
    """Detailed response with content."""
    content: str
    
    class Config:
        from_attributes = True

class WikipediaSectionsResponse(BaseModel):
    """Schema for Wikipedia page sections."""
    sections: Dict[str, str] 
