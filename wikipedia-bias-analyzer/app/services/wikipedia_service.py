import asyncio
import datetime
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session

from app.models.wikipedia import WikipediaPage
from app.core.exceptions import WikipediaError
from app.utils.wiki_parsing import WikipediaProcessor, ContentProcessor

class WikipediaService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.wiki_processor = WikipediaProcessor()
        self.content_processor = ContentProcessor()
    
    def validate_url(self, url: str) -> None:
        """
        Validate if the given URL is a proper Wikipedia URL.
        Raises WikipediaError if the URL is invalid.
        """
        if not self.wiki_processor.validate_url(url):
            raise WikipediaError(f"Invalid Wikipedia URL: {url}")
    
    async def process_url(self, url: str) -> WikipediaPage:
        """
        Process a Wikipedia URL using the existing WikipediaProcessor:
        1. Validate the URL
        2. Fetch and process the content 
        3. Save to database
        """
        # Check if page already exists
        existing_page = self.db_session.query(WikipediaPage).filter(WikipediaPage.url == url).first()
        if existing_page:
            return await self.refresh_page(existing_page.id)
        
        self.validate_url(url)
        
        # Use the existing wiki_processor to fetch content
        # Run this in a thread pool since it uses synchronous requests
        content = await asyncio.to_thread(self.wiki_processor.fetch_content, url)
        
        if not content:
            raise WikipediaError(f"Failed to fetch content from {url}")
        
        # Create a new page
        page = WikipediaPage(
            url=url,
            title=content.basic_info.title,
            content=content.basic_info.text,
            last_fetched=datetime.datetime.utcnow()
        )
        
        self.db_session.add(page)
        self.db_session.commit()
        self.db_session.refresh(page)
        
        return page
    
    async def get_page(self, page_id: int) -> Optional[WikipediaPage]:
        """Retrieve a Wikipedia page by ID."""
        return self.db_session.query(WikipediaPage).filter(WikipediaPage.id == page_id).first()
    
    async def refresh_page(self, page_id: int) -> Optional[WikipediaPage]:
        """
        Refresh the content of an existing Wikipedia page.
        """
        page = await self.get_page(page_id)
        if not page:
            return None
        
        # Use the existing wiki_processor to fetch content
        content = await asyncio.to_thread(self.wiki_processor.fetch_content, page.url)
        
        if not content:
            raise WikipediaError(f"Failed to refresh content from {page.url}")
        
        # Update the page
        page.title = content.basic_info.title
        page.content = content.basic_info.text
        page.last_fetched = datetime.datetime.utcnow()
        
        self.db_session.commit()
        self.db_session.refresh(page)
        
        return page
    
    def get_sections(self, page_id: int) -> Dict[str, str]:
        """
        Get sections for a Wikipedia page using the ContentProcessor.
        """
        page = self.db_session.query(WikipediaPage).filter(WikipediaPage.id == page_id).first()
        if not page:
            raise WikipediaError(f"Wikipedia page with ID {page_id} not found")
        
        # Convert to markdown and split into sections
        markdown_text = self.content_processor.convert_to_markdown(page.content)
        sections = self.content_processor.chunk_content(markdown_text)
        
        return sections 
