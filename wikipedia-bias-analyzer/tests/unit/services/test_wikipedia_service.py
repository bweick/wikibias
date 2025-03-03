import pytest
from unittest.mock import patch, MagicMock, PropertyMock
import datetime

from app.models.wikipedia import WikipediaPage
from app.services.wikipedia_service import WikipediaService
from app.core.exceptions import WikipediaError
from app.utils.wiki_parsing import WikipediaContent, BasicInfo, Metadata, Links

# Add pytest-asyncio markers to test file
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_wiki_processor():
    """Create a mock WikipediaProcessor"""
    mock = MagicMock()
    mock.validate_url.return_value = True
    return mock

@pytest.fixture
def mock_content_processor():
    """Create a mock ContentProcessor"""
    mock = MagicMock()
    mock.convert_to_markdown.return_value = "# Test Markdown"
    mock.chunk_content.return_value = {"Introduction": "Test content", "Section 1": "More content"}
    return mock

@pytest.fixture
def mock_wiki_content():
    """Create a mock WikipediaContent object"""
    return WikipediaContent(
        basic_info=BasicInfo(
            title="Python (programming language)",
            summary="Python is a programming language",
            url="https://en.wikipedia.org/wiki/Python_(programming_language)",
            page_id=123,
            text="Python is a high-level programming language."
        ),
        metadata=Metadata(
            language="en"
        ),
        links=Links(
            categories=["Programming languages", "Software"],
            internal_links=["Computer programming", "Java"],
            languages=["fr", "de"]
        )
    )

@pytest.fixture
def mock_db_session():
    """Create a fully mocked DB session."""
    session = MagicMock()
    session.query.return_value.filter.return_value.first.return_value = None
    return session

@pytest.fixture
def mock_wikipedia_page():
    """Create a mock Wikipedia page for consistent testing."""
    page = MagicMock(spec=WikipediaPage)
    page.id = 1
    page.url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    page.title = "Python (programming language)"
    page.content = "Python is a high-level programming language."
    page.last_fetched = datetime.datetime.utcnow()
    return page

@pytest.fixture
def wikipedia_service(mock_db_session, mock_wiki_processor, mock_content_processor):
    """Create a WikipediaService with mock components."""
    service = WikipediaService(mock_db_session)
    service.wiki_processor = mock_wiki_processor
    service.content_processor = mock_content_processor
    return service

class TestWikipediaService:
    """Tests for the WikipediaService."""

    def test_validate_wikipedia_url_valid(self, wikipedia_service, mock_wiki_processor):
        """Test URL validation with valid Wikipedia URLs."""
        mock_wiki_processor.validate_url.return_value = True
        
        # Should not raise an exception
        wikipedia_service.validate_url("https://en.wikipedia.org/wiki/Python_(programming_language)")
        mock_wiki_processor.validate_url.assert_called_once()

    def test_validate_wikipedia_url_invalid(self, wikipedia_service, mock_wiki_processor):
        """Test URL validation with invalid URLs."""
        mock_wiki_processor.validate_url.return_value = False
        
        with pytest.raises(WikipediaError):
            wikipedia_service.validate_url("https://google.com")
        mock_wiki_processor.validate_url.assert_called_once()

    @patch("asyncio.to_thread")
    @patch("app.services.wikipedia_service.WikipediaPage")
    async def test_process_url_success(
        self, mock_page_class, mock_to_thread, wikipedia_service, mock_db_session, 
        mock_wiki_content, mock_wikipedia_page
    ):
        """Test the full URL processing flow."""
        # Setup mocks
        url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
        mock_to_thread.return_value = mock_wiki_content
        
        # Mock the WikipediaPage class to return our mock_wikipedia_page
        mock_page_class.return_value = mock_wikipedia_page
        
        # Set up db_session to return None for existing page query
        # This simulates no existing page found in the database
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Process the URL
        page = await wikipedia_service.process_url(url)
        
        # Assertions
        assert page is mock_wikipedia_page
        assert page.url == url
        assert page.title == mock_wiki_content.basic_info.title
        assert page.content == mock_wiki_content.basic_info.text
        
        # Ensure proper database interaction
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        
        # Verify the right methods were called
        wikipedia_service.wiki_processor.validate_url.assert_called_once()
        mock_to_thread.assert_called_once()

    @patch("asyncio.to_thread")
    async def test_process_url_fetch_error(
        self, mock_to_thread, wikipedia_service, mock_db_session
    ):
        """Test error handling when fetching Wikipedia content."""
        # Set up db_session to return None for existing page query
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Setup mocks to return None (failed fetch)
        mock_to_thread.return_value = None
        
        # Call the service and check exception
        url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
        with pytest.raises(WikipediaError, match="Failed to fetch content from"):
            await wikipedia_service.process_url(url)

    async def test_get_page_existing(self, wikipedia_service, mock_db_session, mock_wikipedia_page):
        """Test retrieving an existing Wikipedia page."""
        # Setup mock query to return the page
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_wikipedia_page
        
        # Get the page
        result = await wikipedia_service.get_page(1)
        
        # Assertions
        assert result is mock_wikipedia_page
        assert result.id == 1
        assert result.url == mock_wikipedia_page.url
        assert result.title == mock_wikipedia_page.title

    async def test_get_page_nonexistent(self, wikipedia_service, mock_db_session):
        """Test attempting to retrieve a non-existent page."""
        # Setup mock query to return None
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Get the page and expect None
        result = await wikipedia_service.get_page(999)
        assert result is None

    @patch("asyncio.to_thread")
    async def test_refresh_page(
        self, mock_to_thread, wikipedia_service, mock_db_session, mock_wiki_content, mock_wikipedia_page
    ):
        """Test refreshing a Wikipedia page's content."""
        # Setup mock query to return the page
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_wikipedia_page
        
        # Setup content fetch mock
        mock_to_thread.return_value = mock_wiki_content
        
        # Refresh the page
        updated_page = await wikipedia_service.refresh_page(1)
        
        # Assertions
        assert updated_page is mock_wikipedia_page
        # Verify title and content were updated
        assert updated_page.title == mock_wiki_content.basic_info.title
        assert updated_page.content == mock_wiki_content.basic_info.text
        # Verify last_fetched was updated to a recent time
        assert (datetime.datetime.utcnow() - updated_page.last_fetched).total_seconds() < 5
        
        # Ensure proper database interaction
        mock_db_session.commit.assert_called_once()

    def test_get_sections(self, wikipedia_service, mock_db_session, mock_wikipedia_page):
        """Test getting sections from a Wikipedia page."""
        # Mock the database query to return our mock page
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_wikipedia_page
        
        # Mock the content processor methods
        mock_markdown = "# Section 1\nContent 1\n# Section 2\nContent 2"
        wikipedia_service.content_processor.convert_to_markdown.return_value = mock_markdown
        
        mock_sections = {
            "Section 1": "Content 1",
            "Section 2": "Content 2"
        }
        wikipedia_service.content_processor.chunk_content.return_value = mock_sections
        
        # Call the method with a page ID
        sections = wikipedia_service.get_sections(1)
        
        # Verify the result
        assert sections == mock_sections
        # Verify the content processor methods were called correctly
        wikipedia_service.content_processor.convert_to_markdown.assert_called_once_with(mock_wikipedia_page.content)
        wikipedia_service.content_processor.chunk_content.assert_called_once()

