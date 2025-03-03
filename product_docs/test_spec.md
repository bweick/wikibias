# Wikipedia Bias Analyzer Testing Specification

## 1. Testing Philosophy

Our testing strategy for the Wikipedia Bias Analyzer application follows these key principles:

- **Test behavior, not implementation**: Focus on testing what the code does, not how it does it
- **Fast feedback**: Prioritize test speed to enable quick developer iteration
- **Reliability**: Tests should be consistent and avoid flakiness
- **Maintainability**: Tests should be easy to understand and maintain
- **Coverage**: Aim for high test coverage of critical paths

## 2. Test Types

### 2.1 Unit Tests
- Test individual components in isolation
- Mock all external dependencies
- Should be fast and focused

### 2.2 Integration Tests
- Test the interaction between multiple components
- May involve real dependencies for key integrations
- Focus on API contracts and component boundaries

### 2.3 End-to-End Tests
- Test complete user flows from frontend to backend
- Exercise the application as a whole
- Cover critical user journeys

## 3. Database Testing Strategy

After experimenting with different approaches, we recommend the following database testing strategy:

### 3.1 Unit Test Database Strategy
- **Use complete mocking**: For unit tests, mock the database session and all ORM operations
- **No real database connection**: Unit tests should never connect to a real database
- **Test model behavior**: Test model validation, relationships through mocks

### 3.2 Integration Test Database Strategy
- **Test container approach**: Use a dedicated PostgreSQL container for integration tests
- **Docker-based setup**: Use Docker for consistent test environments
- **Isolated test database**: Each test run should use a clean database state
- **Real schema migrations**: Run actual Alembic migrations to verify schema changes

### 3.3 Benefits of this Approach
- Unit tests remain fast and dependency-free
- Integration tests verify actual database behavior with PostgreSQL
- Avoids SQLite/PostgreSQL compatibility issues
- Closer to production environment

## 4. Mocking Strategy

### 4.1 What to Mock
- Database sessions and queries in unit tests
- External APIs and services
- Time-dependent functions
- Resource-intensive operations

### 4.2 How to Mock
- Use pytest fixtures for common mocks
- Use MagicMock for complex behavior
- Create dedicated mock factories for common objects
- Return realistic test data that matches production shapes

### 4.3 Example Mock Pattern
```python
@pytest.fixture
def mock_db_session():
    """Create a fully mocked DB session."""
    session = MagicMock()
    session.query.return_value.filter.return_value.first.return_value = None
    return session

@pytest.fixture
def service_with_mocks(mock_db_session):
    """Create a service with all dependencies mocked."""
    service = SomeService(mock_db_session)
    return service
```

## 5. Model Testing Strategy

### 5.1 Unit Tests for Models
- Test model attributes and relationships with mocks
- Verify validation logic
- Test custom model methods

### 5.2 Integration Tests for Models
- Test actual database interactions
- Verify ORM behavior with real queries
- Test constraints and integrity rules

### 5.3 Example Model Test Pattern

```python
# Unit test with mocks
def test_model_attributes():
    """Test model attributes using mocks."""
    mock_model = MagicMock(spec=SomeModel)
    mock_model.attribute = "value"
    assert mock_model.attribute == "value"

# Integration test with real database
def test_model_persistence(pg_test_db):
    """Test model persistence with a real database."""
    model = SomeModel(attribute="value")
    pg_test_db.add(model)
    pg_test_db.commit()
    
    retrieved = pg_test_db.query(SomeModel).first()
    assert retrieved.attribute == "value"
```

## 6. Test Organization

### 6.1 Directory Structure
```
tests/
├── unit/                # Unit tests
│   ├── models/          # Model unit tests 
│   ├── services/        # Service unit tests
│   └── api/             # API route unit tests
├── integration/         # Integration tests
│   ├── api/             # API integration tests
│   └── database/        # Database integration tests
├── e2e/                 # End-to-end tests
├── conftest.py          # Common fixtures
└── docker-compose.yml   # Test containers
```

### 6.2 Naming Conventions
- File names: `test_<module_name>.py`
- Test functions: `test_<functionality>_<scenario>`
- Test classes: `Test<ComponentName>`

## 7. Setup for PostgreSQL in Testing

### 7.1 Docker Compose Setup
Create a `docker-compose.test.yml` for integration tests:

```yaml
version: '3.8'
services:
  test-db:
    image: postgres:14
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: wikipedia_bias_test
    ports:
      - "5433:5432"  # Use different port to avoid conflicts
```

### 7.2 Test Database Configuration
```python
# In tests/conftest.py for integration tests
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base

# Test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5433/wikipedia_bias_test"
)

@pytest.fixture(scope="session")
def pg_engine():
    """Create a PostgreSQL engine for testing."""
    engine = create_engine(TEST_DATABASE_URL)
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def pg_test_db(pg_engine):
    """Create tables and return a test database session."""
    Base.metadata.create_all(pg_engine)
    Session = sessionmaker(bind=pg_engine)
    session = Session()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(pg_engine)
```

## 8. CI/CD Integration

### 8.1 Recommended CI Pipeline Steps
1. Run linting and code quality checks
2. Run unit tests with mocked database
3. Start test containers
4. Run integration tests against test containers
5. Run end-to-end tests
6. Generate coverage reports

### 8.2 Test Environment Variables
```
TEST_DATABASE_URL=postgresql://postgres:postgres@test-db:5432/wikipedia_bias_test
TEST_API_KEY=test-api-key
# Other test environment variables
```

## 9. Implementation Plan

### 9.1 Short-term Actions
1. Update all unit tests to use consistent mocking pattern
2. Create Docker Compose file for test PostgreSQL
3. Update model integration tests to use PostgreSQL

### 9.2 Medium-term Actions
1. Add integration test suite with real database
2. Implement CI/CD pipeline
3. Increase test coverage
