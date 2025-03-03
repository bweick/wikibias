# Wikipedia Bias Analyzer

A tool for analyzing bias in Wikipedia articles using LLM technology.

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with the following variables:
   ```
   DATABASE_URL=postgresql://username:password@localhost/wikipedia_bias
   OPENAI_API_KEY=your-openai-api-key
   SECRET_KEY=your-secret-key
   DEBUG=True
   ```

4. Initialize the database:
   ```
   alembic upgrade head
   ```

5. Run the application:
   ```
   uvicorn app.main:app --reload
   ```

## API Documentation

Once the application is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Running Tests

```
pytest
``` 
