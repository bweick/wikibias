def test_prompt_model(mock_prompt_template):
    """Test the PromptTemplate model attributes and methods."""
    # Test attributes
    assert mock_prompt_template.id == 1
    assert mock_prompt_template.name == "Test Prompt"
    assert mock_prompt_template.description == "A test prompt template"
    assert mock_prompt_template.prompt_text == "This is a test prompt with {{variable}}."
    assert mock_prompt_template.is_active is True
    assert mock_prompt_template.is_default is False
