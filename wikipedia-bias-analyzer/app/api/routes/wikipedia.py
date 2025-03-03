from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict

from app.core.dependencies import get_db
from app.services.wikipedia_service import WikipediaService
from app.schemas.wikipedia import (
    WikipediaUrlRequest,
    WikipediaPageResponse,
    WikipediaPageDetailResponse,
    WikipediaSectionsResponse
)
from app.core.exceptions import WikipediaError

router = APIRouter(prefix="/wikipedia", tags=["wikipedia"])

def get_wikipedia_service(db: Session = Depends(get_db)) -> WikipediaService:
    """Get an instance of WikipediaService with a database session."""
    return WikipediaService(db_session=db)

@router.post("/pages", response_model=WikipediaPageResponse, status_code=status.HTTP_201_CREATED)
async def process_wikipedia_url(
    request: WikipediaUrlRequest,
    service: WikipediaService = Depends(get_wikipedia_service)
):
    """
    Process a Wikipedia URL:
    1. Validate the URL
    2. Fetch content
    3. Store in database
    """
    try:
        page = await service.process_url(str(request.url))
        return page
    except WikipediaError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing Wikipedia URL: {str(e)}"
        )

@router.get("/pages/{page_id}", response_model=WikipediaPageResponse)
async def get_wikipedia_page(
    page_id: int,
    service: WikipediaService = Depends(get_wikipedia_service)
):
    """Get a Wikipedia page by ID."""
    page = await service.get_page(page_id)
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wikipedia page with ID {page_id} not found"
        )
    return page

@router.put("/pages/{page_id}/refresh", response_model=WikipediaPageResponse)
async def refresh_wikipedia_page(
    page_id: int,
    service: WikipediaService = Depends(get_wikipedia_service)
):
    """Refresh a Wikipedia page's content."""
    try:
        page = await service.refresh_page(page_id)
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wikipedia page with ID {page_id} not found"
            )
        return page
    except WikipediaError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing Wikipedia page: {str(e)}"
        )

@router.get("/pages/{page_id}/sections", response_model=Dict[str, str])
async def get_wikipedia_page_sections(
    page_id: int,
    service: WikipediaService = Depends(get_wikipedia_service)
):
    """Get the sections of a Wikipedia page."""
    try:
        sections = service.get_sections(page_id)
        return sections
    except WikipediaError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting page sections: {str(e)}"
        ) 
