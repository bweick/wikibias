import datetime

def test_wikipedia_page_model(mock_wikipedia_page, mock_bias_analysis):
    """Test the WikipediaPage model attributes and relationships."""
    # Set up the relationship
    mock_wikipedia_page.analyses = [mock_bias_analysis]
    mock_bias_analysis.page = mock_wikipedia_page
    
    # Test attributes
    assert mock_wikipedia_page.id == 1
    assert mock_wikipedia_page.url == "https://en.wikipedia.org/wiki/Python_(programming_language)"
    assert mock_wikipedia_page.title == "Python (programming language)"
    assert "Python" in mock_wikipedia_page.content
    assert isinstance(mock_wikipedia_page.last_fetched, datetime.datetime)
    
    # Test relationships
    assert len(mock_wikipedia_page.analyses) == 1
    assert mock_wikipedia_page.analyses[0] is mock_bias_analysis
    assert mock_bias_analysis.page is mock_wikipedia_page
