def test_root_endpoint(client):
    """Test that the root endpoint returns a welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Wikipedia Bias Analyzer API"}

def test_health_endpoint(client):
    """Test that the health endpoint returns a 200 status code."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"} 
