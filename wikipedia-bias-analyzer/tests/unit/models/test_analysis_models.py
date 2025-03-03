# Use the fixtures from conftest.py
def test_bias_analysis_model(mock_bias_analysis, mock_wikipedia_page, mock_prompt_template):
    """Test that the BiasAnalysis model has the expected attributes."""
    # Set up relationships
    mock_bias_analysis.page = mock_wikipedia_page
    mock_bias_analysis.prompt = mock_prompt_template
    
    # Test attributes
    assert mock_bias_analysis.id == 1
    assert mock_bias_analysis.page_id == 1
    assert mock_bias_analysis.prompt_id == 1
    assert mock_bias_analysis.status == "completed"
    
    # Test relationships
    assert mock_bias_analysis.page is mock_wikipedia_page
    assert mock_bias_analysis.prompt is mock_prompt_template

def test_aggregated_result_model(mock_aggregated_result):
    """Test that the AggregatedResult model has the expected attributes."""
    # Test attributes
    assert mock_aggregated_result.id == 1
    assert mock_aggregated_result.analysis_id == 1
    assert mock_aggregated_result.section_name == "Introduction"
    assert "phrase1" in mock_aggregated_result.biased_phrases
    assert len(mock_aggregated_result.heatmap_data) == 1
    assert mock_aggregated_result.heatmap_data[0]["score"] == 0.8

def test_bias_result_model(mock_bias_result):
    """Test that the BiasResult model has the expected attributes."""
    # Test attributes
    assert mock_bias_result.id == 1
    assert mock_bias_result.aggregated_result_id == 1
    assert mock_bias_result.section_name == "Introduction"
    assert mock_bias_result.iteration == 1

def test_bias_instance_model(mock_bias_instance):
    """Test that the BiasInstance model has the expected attributes."""
    # Test attributes
    assert mock_bias_instance.id == 1
    assert mock_bias_instance.result_id == 1
    assert mock_bias_instance.bias_type == "Political"
    assert "political bias" in mock_bias_instance.rationale.lower()

def test_model_relationships(mock_related_models):
    """Test the relationships between models."""
    # Extract models from fixture
    analysis = mock_related_models['analysis']
    agg_result = mock_related_models['agg_result']
    bias_result = mock_related_models['bias_result']
    bias_instance = mock_related_models['bias_instance']
    page = mock_related_models['page']
    
    # Test relationship chain
    assert analysis.page is page
    assert analysis.aggregated_results[0] is agg_result
    assert agg_result.analysis is analysis
    assert agg_result.results[0] is bias_result
    assert bias_result.aggregated_result is agg_result
    assert bias_result.bias_instances[0] is bias_instance
    assert bias_instance.result is bias_result


