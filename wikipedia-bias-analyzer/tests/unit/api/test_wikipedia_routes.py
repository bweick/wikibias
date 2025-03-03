import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import status
from fastapi.testclient import TestClient
import datetime

from app.main import app
from app.models.wikipedia import WikipediaPage

# Test client for making requests
client = TestClient(app)

# Use a complete patch for dependency override
@pytest.fixture(autouse=True)
def override_dependency():
    """Override the get_db dependency completely."""
    with patch("app.api.routes.wikipedia.get_db", autospec=True):
        yield

class TestWikipediaRoutes:
    """Tests for Wikipedia API endpoints."""
    
    @patch("app.api.routes.wikipedia.get_wikipedia_service")
    async def test_process_wikipedia_url(self, mock_get_service):
        """Test processing a Wikipedia URL."""
        # Setup mock service and response
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        
        # Create a simple dict instead of a model instance
        mock_page = {
            "id": 1,
            "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
            "title": "Python (programming language)",
            "last_fetched": datetime.datetime.utcnow().isoformat()
        }
        
        # Return the dict instead of a model
        mock_service.process_url.return_value = MagicMock(**mock_page)
        
        # Make request
        response = client.post(
            "/api/wikipedia/pages",
            json={"url": "https://en.wikipedia.org/wiki/Python_(programming_language)"}
        )
        
        # Assertions
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["id"] == 1
        assert response.json()["url"] == "https://en.wikipedia.org/wiki/Python_(programming_language)"
        assert response.json()["title"] == "Python (programming language)"
    
    @patch("app.api.routes.wikipedia.get_wikipedia_service")
    async def test_get_wikipedia_page(self, mock_get_service):
        """Test retrieving a Wikipedia page by ID."""
        # Setup mock service and response
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        
        mock_page = WikipediaPage(
            id=1,
            url="https://en.wikipedia.org/wiki/Python_(programming_language)",
            title="Python (programming language)",
            content="Content about Python",
            last_fetched=datetime.datetime.utcnow()
        )
        mock_service.get_page.return_value = mock_page
        
        # Make request
        response = client.get("/api/wikipedia/pages/1")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == 1
        assert response.json()["url"] == "https://en.wikipedia.org/wiki/Python_(programming_language)"
        assert response.json()["title"] == "Python (programming language)"
        mock_service.get_page.assert_called_once_with(1)
    
    @patch("app.api.routes.wikipedia.get_wikipedia_service")
    async def test_get_wikipedia_page_not_found(self, mock_get_service):
        """Test retrieving a non-existent Wikipedia page."""
        # Setup mock service to return None (page not found)
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        mock_service.get_page.return_value = None
        
        # Make request
        response = client.get("/api/wikipedia/pages/999")
        
        # Assertions
        assert response.status_code == status.HTTP_404_NOT_FOUND
        mock_service.get_page.assert_called_once_with(999)
    
    @patch("app.api.routes.wikipedia.get_wikipedia_service")
    async def test_refresh_wikipedia_page(self, mock_get_service):
        """Test refreshing a Wikipedia page."""
        # Setup mock service and response
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        
        mock_page = WikipediaPage(
            id=1,
            url="https://en.wikipedia.org/wiki/Python_(programming_language)",
            title="Python (programming language)",
            content="Updated content about Python",
            last_fetched=datetime.datetime.utcnow()
        )
        mock_service.refresh_page.return_value = mock_page
        
        # Make request
        response = client.put("/api/wikipedia/pages/1/refresh")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == 1
        assert "Updated content" not in response.json()  # Content should not be returned
        mock_service.refresh_page.assert_called_once_with(1)
    
    @patch("app.api.routes.wikipedia.get_wikipedia_service")
    async def test_refresh_wikipedia_page_not_found(self, mock_get_service):
        """Test refreshing a non-existent Wikipedia page."""
        # Setup mock service to return None (page not found)
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        mock_service.refresh_page.return_value = None
        
        # Make request
        response = client.put("/api/wikipedia/pages/999/refresh")
        
        # Assertions
        assert response.status_code == status.HTTP_404_NOT_FOUND
        mock_service.refresh_page.assert_called_once_with(999)
    
    @patch("app.api.routes.wikipedia.get_wikipedia_service")
    async def test_get_wikipedia_page_sections(self, mock_get_service):
        """Test getting sections of a Wikipedia page."""
        # Setup mock service and response
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        
        mock_sections = {
            "Introduction": "This is an introduction.",
            "History": "This is the history section.",
            "Features": "These are the features."
        }
        mock_service.get_sections.return_value = mock_sections
        
        # Make request
        response = client.get("/api/wikipedia/pages/1/sections")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        sections = response.json()
        assert sections["Introduction"] == "This is an introduction."
        assert sections["History"] == "This is the history section."
        assert sections["Features"] == "These are the features."
        mock_service.get_sections.assert_called_once_with(1)
    
    @patch("app.api.routes.wikipedia.get_wikipedia_service")
    async def test_get_wikipedia_page_sections_not_found(self, mock_get_service):
        """Test getting sections of a non-existent Wikipedia page."""
        # Setup mock service to raise WikipediaError
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.get_sections.side_effect = Exception("Wikipedia page with ID 999 not found")
        
        # Make request
        response = client.get("/api/wikipedia/pages/999/sections")
        
        # Assertions
        assert response.status_code == status.HTTP_404_NOT_FOUND
        mock_service.get_sections.assert_called_once_with(999) 
