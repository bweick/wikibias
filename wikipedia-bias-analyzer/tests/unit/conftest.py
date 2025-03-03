import pytest
from unittest.mock import MagicMock
import datetime

from app.models.wikipedia import WikipediaPage
from app.models.prompt import PromptTemplate
from app.models.analysis import (
    BiasAnalysis, 
    AggregatedResult, 
    BiasResult, 
    BiasInstance
)

@pytest.fixture
def mock_db_session():
    """Create a fully mocked DB session."""
    session = MagicMock()
    # Default return values for common query patterns
    session.query.return_value.filter.return_value.first.return_value = None
    session.query.return_value.all.return_value = []
    return session

@pytest.fixture
def mock_wikipedia_page():
    """Create a mock Wikipedia page."""
    page = MagicMock(spec=WikipediaPage)
    page.id = 1
    page.url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    page.title = "Python (programming language)"
    page.content = "Python is a high-level programming language..."
    page.last_fetched = datetime.datetime.now()
    page.analyses = []
    
    return page

@pytest.fixture
def mock_prompt_template():
    """Create a mock prompt template."""
    prompt = MagicMock(spec=PromptTemplate)
    prompt.id = 1
    prompt.name = "Test Prompt"
    prompt.description = "A test prompt template"
    prompt.prompt_text = "This is a test prompt with {{variable}}."
    prompt.is_active = True
    prompt.is_default = False
    
    return prompt

@pytest.fixture
def mock_bias_analysis():
    """Create a mock bias analysis."""
    analysis = MagicMock(spec=BiasAnalysis)
    analysis.id = 1
    analysis.page_id = 1
    analysis.prompt_id = 1
    analysis.status = "completed"
    analysis.created_at = datetime.datetime.now()
    analysis.aggregated_results = []
    
    return analysis

@pytest.fixture
def mock_aggregated_result():
    """Create a mock aggregated result."""
    agg_result = MagicMock(spec=AggregatedResult)
    agg_result.id = 1
    agg_result.analysis_id = 1
    agg_result.section_name = "Introduction"
    agg_result.biased_phrases = {"phrase1": 2, "phrase2": 1}
    agg_result.heatmap_data = [{"start": 0, "end": 10, "score": 0.8}]
    agg_result.results = []
    
    return agg_result

@pytest.fixture
def mock_bias_result():
    """Create a mock bias result."""
    bias_result = MagicMock(spec=BiasResult)
    bias_result.id = 1
    bias_result.aggregated_result_id = 1
    bias_result.section_name = "Introduction"
    bias_result.section_content = "This is the section content."
    bias_result.iteration = 1
    bias_result.raw_llm_response = "Raw LLM response here."
    bias_result.bias_instances = []
    
    return bias_result

@pytest.fixture
def mock_bias_instance():
    """Create a mock bias instance."""
    bias_instance = MagicMock(spec=BiasInstance)
    bias_instance.id = 1
    bias_instance.result_id = 1
    bias_instance.bias_type = "Political"
    bias_instance.rationale = "This shows political bias because..."
    bias_instance.affected_stakeholder = "Political group"
    bias_instance.biased_phrase = "controversial policy"
    
    return bias_instance

@pytest.fixture
def mock_related_models(mock_wikipedia_page, mock_prompt_template, mock_bias_analysis, 
                         mock_aggregated_result, mock_bias_result, mock_bias_instance):
    """Create a set of related model instances with proper relationships."""
    # Set up relationships
    mock_bias_analysis.page = mock_wikipedia_page
    mock_bias_analysis.prompt = mock_prompt_template
    mock_wikipedia_page.analyses = [mock_bias_analysis]
    
    mock_aggregated_result.analysis = mock_bias_analysis
    mock_bias_analysis.aggregated_results = [mock_aggregated_result]
    
    mock_bias_result.aggregated_result = mock_aggregated_result
    mock_aggregated_result.results = [mock_bias_result]
    
    mock_bias_instance.result = mock_bias_result
    mock_bias_result.bias_instances = [mock_bias_instance]
    
    return {
        'page': mock_wikipedia_page,
        'prompt': mock_prompt_template,
        'analysis': mock_bias_analysis,
        'agg_result': mock_aggregated_result,
        'bias_result': mock_bias_result,
        'bias_instance': mock_bias_instance
    } 
