import wikipediaapi
from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from urllib.parse import urlparse
import re
from markdownify import markdownify as md
import os
from dotenv import load_dotenv
load_dotenv()

class BasicInfo(BaseModel):
    title: str
    summary: str
    url: str
    page_id: int
    text: str
class Metadata(BaseModel):
    language: str

class Links(BaseModel):
    categories: list[str]
    internal_links: list[str]
    languages: list[str]

class WikipediaContent(BaseModel):
    """Pydantic model for storing Wikipedia content"""
    basic_info: BasicInfo
    metadata: Metadata
    links: Links

class WikipediaProcessor:
    def __init__(self):
        # Initialize with English Wikipedia
        self.wiki = wikipediaapi.Wikipedia(
            language='en',
            extract_format=wikipediaapi.ExtractFormat.HTML,
            user_agent='BiasAnalyzer/1.0 (your@email.com)'  # Replace with your email
        )

    def extract_page_title_from_url(self, url: str) -> str:
        """Extract the page title from a Wikipedia URL"""
        parsed_url = urlparse(url)
        if 'wikipedia.org' not in parsed_url.netloc:
            raise ValueError("Not a valid Wikipedia URL")
        
        # Extract the title from the path
        path_parts = parsed_url.path.split('/')
        # Wikipedia URLs typically have format /wiki/Page_Title
        if len(path_parts) < 3 or path_parts[1] != 'wiki':
            raise ValueError("Invalid Wikipedia URL format")
        
        return path_parts[2]

    def fetch_content(self, url: str) -> Optional[WikipediaContent]:
        """Get more detailed content from a Wikipedia page"""
        try:
            page_title = self.extract_page_title_from_url(url)
            page = self.wiki.page(page_title)
            print(page.__getattr__("text"))
            # Save page data as JSON for testing
            # import json
            # import os
            
            # test_fixtures_dir = os.path.join("wikipedia-bias-analyzer","tests", "fixtures")
            # os.makedirs(test_fixtures_dir, exist_ok=True)
            
            # with open(os.path.join(test_fixtures_dir, "python_page.json"), "w") as f:
            #     json.dump(page.__dict__, f, indent=2)
            
            if not page.exists():
                return None
            
            return WikipediaContent(
                basic_info=BasicInfo(
                    title=page.title,
                    summary=page.summary,
                    url=url,  # Use the original URL passed to the function
                    page_id=page.pageid,
                    text=page.text,
                ),
                metadata=Metadata(
                    language=page.language,
                ),
                links=Links(
                    categories=list(page.categories.keys()),
                    internal_links=list(page.links.keys())[:10],  # First 10 links
                    languages=list(page.langlinks.keys()),
                )
            )
            
        except Exception as e:
            raise Exception(f"Error fetching Wikipedia content: {str(e)}")

    def validate_url(self, url: str) -> bool:
        """Validate if the given URL is a valid Wikipedia URL"""
        try:
            parsed_url = urlparse(url)
            return (
                parsed_url.scheme in ('http', 'https') and
                'wikipedia.org' in parsed_url.netloc and
                '/wiki/' in parsed_url.path
            )
        except Exception:
            return False

class ContentProcessor:
    def __init__(self):
        self.chunk_size = 8000  # Adjustable chunk size for API processing
        self.wiki_processor = WikipediaProcessor()
    
    def get_and_process_content(self, url: str) -> WikipediaContent:
        if self.wiki_processor.validate_url(url):
            content = self.wiki_processor.fetch_content(url)
            if content:
                # Convert to markdown

                markdown_content = self.convert_to_markdown(content)
                print("\nConverted Markdown Content (preview):")
                # print(markdown_content + "...\n")
                # print(len(markdown_content))
                
                # Show chunks
                chunks = self.chunk_content(markdown_content)
                return chunks
        return None

    def convert_to_markdown(self, content: WikipediaContent) -> str:
        """Convert the Wikipedia HTML content to markdown format"""
        # Configure basic markdownify options
        markdown_options = {
            'heading_style': 'ATX',  # Use # style headers
            'bullets': '-',          # Use - for unordered lists
        }
        
        # Convert HTML content to markdown
        markdown_text = md(content.basic_info.text, **markdown_options)

        # Clean up reference numbers and extra whitespace
        markdown_text = re.sub(r'\[\d+\]', '', markdown_text)
        markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
        
        return markdown_text.strip()

    def chunk_content(self, markdown_text: str) -> Dict[str, str]:
        """Split content into sections based on headers for section-by-section analysis"""
        sections = {}
        current_section = "Introduction"  # Default section for content before first header
        current_content = []
        
        # Split by paragraphs while preserving headers
        paragraphs = markdown_text.split('\n\n')
        
        for paragraph in paragraphs:
            # Check if paragraph is a header
            if paragraph.startswith('#'):
                # Save previous section if it has content
                if current_content:
                    sections[current_section] = '\n\n'.join(current_content)
                    current_content = []
                
                # Update current section title (remove #s and whitespace)
                current_section = paragraph.lstrip('#').strip()
            else:
                current_content.append(paragraph)
        
        # Add the last section if it has content
        if current_content:
            sections[current_section] = '\n\n'.join(current_content)
        
        return sections
