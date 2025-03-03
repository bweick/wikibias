# Backend Specification: Wikipedia Bias Analyzer

## Overview

This document outlines the backend architecture and implementation plan for a web application that analyzes Wikipedia content for bias. The application will:

1. Extract content from Wikipedia pages
2. Process and chunk the content into sections
3. Analyze each section for bias using multiple LLM calls
4. Aggregate and store results
5. Provide an API for the frontend to display results including bias "heat maps"

## Tech Stack

- **Language**: Python 3.10+
- **Web Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **LLM Integration**: OpenAI API (with flexibility to support other providers)
- **Task Queue**: Changy (PostgreSQL-based async task queue)
- **Testing**: pytest
- **Documentation**: Swagger/OpenAPI

## System Architecture

### Components

1. **API Layer**
   - FastAPI application handling HTTP requests
   - Authentication middleware
   - Request validation
   - Response formatting

2. **Service Layer**
   - Wikipedia content fetching service
   - Content processing service
   - Bias analysis service
   - Result aggregation service

3. **Data Layer**
   - Database models
   - Repository pattern for data access
   - Caching mechanism

4. **Background Processing**
   - Changy task queue for handling LLM requests
   - Task scheduling and monitoring
   - PostgreSQL for task storage and state management

5. **Admin Interface**
   - Lightweight admin dashboard for managing prompts
   - Analysis monitoring and management
   - User management for admin access
   - Built with React and integrated with the API

### Data Models

1. **WikipediaPage**
   - URL
   - Title
   - Page ID
   - Raw content
   - Fetch date
   - Relationships: Has many BiasAnalyses

2. **PromptTemplate**
   - ID
   - Name
   - Description
   - Prompt text
   - Created date
   - Modified date
   - Active status
   - Default flag

3. **BiasAnalysis**
   - ID
   - Wikipedia page reference
   - Prompt reference
   - Status (pending, processing, completed, failed)
   - Created date
   - Completion time
   - Relationships: Belongs to WikipediaPage, Has many AggregatedResults

4. **AggregatedResult** 
   - Analysis reference
   - Section name
   - Biased phrases (JSON with phrase and occurrence counts)
   - Heat map data (JSON with visualization data)
   - Result metadata (JSON with additional information)
   - Created/Updated timestamps
   - Relationships: Belongs to BiasAnalysis, Has many BiasResults

5. **BiasResult**
   - AggregatedResult reference
   - Section name
   - Section content
   - Iteration number (1-10)
   - Raw LLM response
   - Processed results (JSON)
   - Processing timestamp
   - Relationships: Belongs to AggregatedResult, Has many BiasInstances

6. **BiasInstance**
   - Result reference
   - Bias type (e.g., "Affective Bias", "Framing Bias")
   - Rationale (explanation of why this is biased)
   - Affected stakeholder (group or entity affected by the bias)
   - Biased phrase (the exact text that contains bias)
   - Start index (position in text where bias starts, optional)
   - End index (position in text where bias ends, optional)
   - Relationships: Belongs to BiasResult

## Data Structures

### BiasInstance
```json
{
  "bias_id": 12,
  "bias_type": "Affective Bias",
  "rationale": "Explanation of why this is biased",
  "affected_stakeholder": "Group or entity affected by the bias",
  "biased_phrase": "The exact text that contains bias"
}
```

### BiasPhrase
```json
{
  "phrase": "Text identified as biased",
  "occurrence_count": 8,
  "index": 145,
  "bias_instances": [12, 23, 45]
}
```

### HeatmapEntry
```json
{
  "start_index": 145,
  "end_index": 169,
  "phrase": "Text identified as biased",
  "intensity": 8,
  "bias_instances": [12, 23, 45]
}
```

### Section
```json
{
  "name": "Section title",
  "content": "Full text content of the section",
  "order": 1,
  "bias_phrases": [
    // BiasPhrase objects
  ]
}
```

## API Endpoints

### Wikipedia Content

- `POST /api/wikipedia/process` - Validate, fetch and process Wikipedia URL (returns page_id)
  - Request:
    ```json
    {
      "url": "https://en.wikipedia.org/wiki/Example_Page"
    }
    ```
  - Response:
    ```json
    {
      "page_id": 123,
      "title": "Example Page",
      "sections": ["Introduction", "History", "Controversy"],
      "url": "https://en.wikipedia.org/wiki/Example_Page",
      "fetch_timestamp": "2023-06-15T12:34:56Z"
    }
    ```

- `GET /api/wikipedia/{page_id}` - Get stored Wikipedia page data
  - Response:
    ```json
    {
      "page_id": 123,
      "title": "Example Page",
      "url": "https://en.wikipedia.org/wiki/Example_Page",
      "sections": [
        {
          "name": "Introduction",
          "content": "This is the introduction text...",
          "order": 1
        },
        {
          "name": "History",
          "content": "Historical information...",
          "order": 2
        }
      ],
      "metadata": {
        "fetch_timestamp": "2023-06-15T12:34:56Z",
        "version_id": "1234567",
        "language": "en"
      }
    }
    ```

### Analysis

- `POST /api/analysis/start` - Start a new bias analysis
  - Request:
    ```json
    {
      "page_id": 123,
      "prompt_id": 456,
      "iterations": 10
    }
    ```
  - Response:
    ```json
    {
      "analysis_id": 789,
      "status": "pending",
      "created_at": "2023-06-15T12:40:00Z",
      "estimated_completion_time": "2023-06-15T12:50:00Z"
    }
    ```

- `GET /api/analysis/{analysis_id}` - Get analysis status and results
  - Response:
    ```json
    {
      "analysis_id": 789,
      "page_id": 123,
      "prompt_id": 456,
      "status": "in-progress",
      "created_at": "2023-06-15T12:40:00Z",
      "updated_at": "2023-06-15T12:45:00Z",
      "progress": {
        "total_sections": 5,
        "completed_sections": 3,
        "percent_complete": 60
      },
      "estimated_completion_time": "2023-06-15T12:50:00Z"
    }
    ```

- `GET /api/analysis/list` - List analyses with pagination and filters
  - Query Parameters:
    - `page`: Page number (default: 1)
    - `limit`: Items per page (default: 20)
    - `status`: Filter by status (pending, in-progress, completed, failed)
  - Response:
    ```json
    {
      "total": 45,
      "page": 1,
      "limit": 20,
      "items": [
        {
          "analysis_id": 789,
          "page_title": "Example Page",
          "status": "completed",
          "created_at": "2023-06-15T12:40:00Z",
          "completed_at": "2023-06-15T12:50:00Z"
        }
      ]
    }
    ```

### Prompts

- `GET /api/prompts` - List available prompts
  - Response:
    ```json
    {
      "prompts": [
        {
          "prompt_id": 456,
          "name": "Standard Bias Analysis",
          "description": "Detects framing, negation, and affective bias",
          "created_at": "2023-05-01T10:00:00Z",
          "is_default": true
        }
      ]
    }
    ```

- `POST /api/prompts` - Create a new prompt
- `PUT /api/prompts/{prompt_id}` - Update a prompt
- `DELETE /api/prompts/{prompt_id}` - Delete a prompt

### Results

### Results

- `GET /api/results/{analysis_id}` - Get aggregated results
  - Response:
    ```json
    {
      "analysis_id": 789,
      "page_id": 123,
      "page_title": "Example Page",
      "prompt": {
        "prompt_id": 456,
        "name": "Standard Bias Analysis",
        "description": "Detects framing, negation, and affective bias"
      },
      "metadata": {
        "iterations": 10,
        "completed_at": "2023-06-15T12:50:00Z",
        "page_version": "1234567",
        "page_fetch_timestamp": "2023-06-15T12:34:56Z"
      },
      "sections": [
        {
          "name": "Introduction",
          "bias_count": 5,
          "bias_phrases": [
            {
              "phrase": "devastating consequences",
              "occurrence_count": 8,
              "index": 145,
              "bias_instances": [12, 23, 45]
            }
          ]
        }
      ],
      "bias_instances": [
        {
          "bias_id": 12,
          "bias_type": "Affective Bias",
          "rationale": "The term 'devastating' is emotionally charged and may overstate the impact.",
          "affected_stakeholder": "Readers seeking objective information",
          "biased_phrase": "devastating consequences"
        }
      ]
    }
    ```

- `GET /api/results/{analysis_id}/heatmap` - Get heat map data
  - Query Parameters:
    - `section`: Section name (optional, returns all sections if omitted)
  - Response:
    ```json
    {
      "analysis_id": 789,
      "section": "Introduction",
      "content": "This is the introduction text with some potentially biased content...",
      "heatmap_data": [
        {
          "start_index": 145,
          "end_index": 169,
          "phrase": "devastating consequences",
          "intensity": 8,
          "bias_instances": [12, 23, 45]
        }
      ]
    }
    ```

- `GET /api/results/{analysis_id}/raw` - Get raw LLM responses
  - Query Parameters:
    - `section`: Section name (required)
    - `iteration`: Iteration number (optional)
  - Response:
    ```json
    {
      "analysis_id": 789,
      "section": "Introduction",
      "iterations": [
        {
          "iteration": 1,
          "timestamp": "2023-06-15T12:41:00Z",
          "methodology": "Semantic analysis of framing, negation, and affective bias",
          "detected_biases": [
            {
              "bias_type": "Affective Bias",
              "rationale": "The term 'devastating' is emotionally charged and may overstate the impact.",
              "affected_stakeholder": "Readers seeking objective information",
              "biased_phrase": "devastating consequences"
            }
          ]
        }
      ]
    }
    ```

### Admin API

- `POST /api/admin/login` - Admin authentication
  - Request:
    ```json
    {
      "username": "admin",
      "password": "secure_password"
    }
    ```
  - Response:
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer",
      "expires_in": 3600
    }
    ```

- `GET /api/admin/dashboard` - Get admin dashboard statistics
  - Response:
    ```json
    {
      "total_analyses": 245,
      "analyses_today": 12,
      "active_analyses": 3,
      "failed_analyses": 2,
      "average_completion_time": 180,
      "prompt_usage": [
        {"prompt_id": 1, "name": "Standard", "usage_count": 156},
        {"prompt_id": 2, "name": "Detailed", "usage_count": 89}
      ]
    }
    ```

- `GET /api/admin/analyses` - Get detailed analysis list with filtering
  - Query Parameters:
    - `status`: Filter by status
    - `date_from`: Filter by start date
    - `date_to`: Filter by end date
    - `page`: Page number
    - `limit`: Items per page
  - Response: (Similar to regular analysis list but with more details)

- `POST /api/admin/analyses/{analysis_id}/cancel` - Cancel an in-progress analysis
- `POST /api/admin/analyses/{analysis_id}/retry` - Retry a failed analysis

## Processing Flow

1. **Content Acquisition**
   - Validate Wikipedia URL
   - Fetch content using WikipediaProcessor
   - Store raw content in database
   - Process and chunk content into sections
   - Store processed content
   - Return page_id for subsequent analysis

2. **Bias Analysis**
   - Create analysis record
   - For each section:
     - Create 10 Changy tasks for LLM processing
     - Each task uses the same prompt but may get different results
     - Store raw responses and extracted biases

3. **Result Aggregation**
   - Count occurrences of each biased phrase across iterations
   - Generate heat map data
   - Store aggregated results
   - Update analysis status to completed

4. **Result Retrieval**
   - Provide endpoints for frontend to fetch results
   - Include metadata about prompt and Wikipedia page version

## Implementation Plan

### Phase 1: Core Infrastructure

1. Set up project structure and dependencies
2. Implement database models and migrations
   - Configure Alembic for database migrations
   - Create initial migration scripts
   - Set up database versioning
3. Set up FastAPI application skeleton
4. Implement authentication and basic middleware
5. Configure Changy for task processing
6. Implement error handling framework
   - Set up global exception handlers
   - Define error response format
   - Create custom exceptions

### Phase 2: Wikipedia Integration

1. Integrate existing WikipediaProcessor
2. Implement content chunking and storage
3. Create API endpoints for Wikipedia content
4. Implement Wikipedia content caching
   - Version tracking for Wikipedia pages
   - Cache invalidation strategy
   - Refresh mechanisms

### Phase 3: LLM Integration

1. Set up Changy workers
2. Implement prompt management
3. Create bias analysis service
   - Implement retry mechanism for LLM calls
   - Handle LLM-specific errors
4. Implement result storage and aggregation
5. Develop analysis results caching
   - Composite cache keys
   - User-controlled cache usage

### Phase 4: API Completion

1. Implement remaining API endpoints
2. Add comprehensive error handling
3. Implement caching for performance
   - HTTP response caching
   - Application-level caching
4. Add pagination and filtering

### Phase 5: Admin Interface

1. Set up React project structure
2. Implement authentication and user management
3. Create dashboard and statistics views
4. Build prompt management interface
5. Implement analysis monitoring and management
6. Add user management features
7. Integrate with backend API
8. Test and secure the admin interface

### Phase 6: Testing and Documentation

1. Write unit and integration tests
   - Test database migrations
   - Test error handling
   - Test caching mechanisms
2. Create API documentation
3. Performance testing and optimization
   - Cache efficiency testing
   - Load testing
4. Security review
   - Authentication/authorization testing
   - Input validation testing
   - Rate limiting implementation

### Phase 7: Deployment and Monitoring

1. Set up Heroku deployment pipeline
2. Configure environment variables and add-ons
3. Implement logging and monitoring
   - Error tracking
   - Performance metrics
   - Cache hit/miss statistics
4. Create backup and recovery procedures
5. Implement data retention policies

## Development Timeline

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| 1: Core Infrastructure | 2 weeks | Project skeleton, DB setup, Auth |
| 2: Wikipedia Integration | 2 weeks | Content fetching, processing, storage |
| 3: LLM Integration | 3 weeks | Bias analysis, result aggregation |
| 4: API Completion | 2 weeks | Full API functionality, caching |
| 5: Admin Interface | 3 weeks | Admin dashboard, prompt management |
| 6: Testing and Documentation | 2 weeks | Tests, docs, performance optimization |
| 7: Deployment and Monitoring | 1 week | Production deployment, monitoring |

**Total Estimated Timeline: 15 weeks**

## Deployment Considerations

1. **Environment Configuration**
   - Use environment variables for configuration
   - Separate development, staging, and production configs
   - Store sensitive configuration in Heroku Config Vars

2. **Heroku Deployment**
   - **Procfile**: Define process types for the application:
     - `web`: Running the FastAPI application with Uvicorn
     - `worker`: Running Changy workers for background tasks
   - **Add-ons**:
     - Heroku Postgres for database and task queue
     - Papertrail for log management
   - **Scaling**: Utilize Heroku's dyno scaling for handling increased load
   - **Release Pipeline**: Implement CI/CD with GitHub Actions or Heroku CI
   - **Development Workflow**: Use local development environment with virtualenv

3. **Scaling**
   - Vertical scaling with Heroku dyno types
   - Horizontal scaling by increasing dyno count
   - Worker pool scaling for Changy
   - Database connection pooling

4. **Monitoring**
   - Application metrics with Heroku metrics dashboard
   - Error tracking with Sentry
   - Performance monitoring with New Relic (optional)

## Development Guidelines

1. **Code Organization**
   - Follow repository pattern
   - Separate concerns (controllers, services, repositories)
   - Use dependency injection

2. **Error Handling**
   - Consistent error responses
   - Detailed logging
   - Graceful degradation

3. **Testing**
   - Unit tests for business logic
   - Integration tests for API endpoints
   - Mock external services

4. **Documentation**
   - Inline code documentation
   - API documentation with examples
   - Setup and deployment instructions

## Admin Interface

### Overview

The admin interface will be a lightweight, secure dashboard for managing the application. It will be built as a single-page application using React and will communicate with the backend via the Admin API endpoints.

### Features

1. **Authentication**
   - Secure login for admin users
   - JWT-based authentication
   - Session management

2. **Dashboard**
   - Overview of system statistics
   - Recent analyses
   - Error rates and performance metrics
   - Quick access to common tasks

3. **Prompt Management**
   - Create, edit, and delete analysis prompts
   - Set default prompts
   - View prompt usage statistics
   - Test prompts on sample content

4. **Analysis Management**
   - View all analyses with filtering and sorting
   - Monitor in-progress analyses
   - Cancel running analyses
   - Retry failed analyses
   - View detailed results and raw LLM responses

5. **User Management**
   - Create and manage admin users
   - Set permissions and access levels

### Implementation

1. **Frontend**
   - React-based SPA
   - Material-UI or similar component library
   - Redux for state management
   - Axios for API communication

2. **Authentication**
   - JWT tokens stored in HTTP-only cookies
   - CSRF protection
   - Role-based access control

3. **Security**
   - All admin routes protected by authentication
   - Rate limiting on login attempts
   - Audit logging for admin actions

## Error Handling Strategy

### Principles

1. **Consistent Error Responses**: All API endpoints will return errors in a standardized format:
   ```json
   {
     "error": {
       "code": "ERROR_CODE",
       "message": "Human-readable error message",
       "details": {}, // Optional additional context
       "request_id": "unique-request-id"
     }
   }
   ```

2. **Error Categorization**:
   - **Client Errors** (4xx): Invalid requests, authentication issues, rate limiting
   - **Server Errors** (5xx): Internal failures, dependency issues
   - **LLM-specific Errors**: Separate category for LLM provider issues

3. **Graceful Degradation**: The system will attempt to continue operation in a degraded state rather than failing completely when possible.

### Error Codes

1. **General Errors**:
   - `INVALID_REQUEST`: Malformed request or invalid parameters
   - `UNAUTHORIZED`: Authentication required or invalid credentials
   - `FORBIDDEN`: Authenticated but insufficient permissions
   - `NOT_FOUND`: Requested resource does not exist
   - `RATE_LIMITED`: Too many requests

2. **Wikipedia-specific Errors**:
   - `WIKI_INVALID_URL`: Invalid Wikipedia URL
   - `WIKI_PAGE_NOT_FOUND`: Wikipedia page does not exist
   - `WIKI_FETCH_ERROR`: Error fetching Wikipedia content
   - `WIKI_PARSE_ERROR`: Error parsing Wikipedia content

3. **Analysis Errors**:
   - `ANALYSIS_INVALID_PARAMS`: Invalid analysis parameters
   - `ANALYSIS_NOT_FOUND`: Analysis does not exist
   - `ANALYSIS_ALREADY_RUNNING`: Analysis is already in progress
   - `ANALYSIS_FAILED`: Analysis failed to complete

4. **LLM Errors**:
   - `LLM_UNAVAILABLE`: LLM provider is unavailable
   - `LLM_RATE_LIMITED`: LLM provider rate limit reached
   - `LLM_CONTEXT_EXCEEDED`: Content exceeds LLM context window
   - `LLM_INVALID_RESPONSE`: LLM response could not be parsed

### Error Handling Implementation

1. **Global Exception Handlers**:
   - FastAPI exception handlers for different error types
   - Automatic conversion of exceptions to standardized error responses

2. **Logging**:
   - All errors logged with context and stack traces
   - Request IDs included in logs for correlation
   - Different log levels based on error severity

3. **Retry Mechanism**:
   - Automatic retry for transient errors (e.g., LLM timeouts)
   - Exponential backoff strategy
   - Maximum retry attempts configurable per error type

4. **Client Feedback**:
   - Clear error messages suitable for display to end users
   - Actionable suggestions where appropriate
   - Technical details hidden from users but available in logs

## Database Migration Strategy

### Technology

- **Alembic**: SQLAlchemy's migration tool for managing database schema changes
- **Migration Scripts**: Auto-generated and manually adjusted for complex changes
- **Version Control**: Migrations tracked in version control alongside code

### Migration Workflow

1. **Development Process**:
   - Developers create model changes in SQLAlchemy models
   - Alembic auto-generates migration scripts (`alembic revision --autogenerate`)
   - Developers review and adjust scripts as needed
   - Migration scripts committed to version control

2. **Testing**:
   - Migrations tested on development databases
   - CI pipeline includes migration testing on fresh database
   - Rollback procedures tested for each migration

3. **Deployment**:
   - Migrations run automatically during deployment
   - Zero-downtime migrations preferred when possible
   - Fallback procedures documented for failed migrations

### Database Versioning

1. **Version Tracking**:
   - Database schema version tracked in dedicated table
   - Application checks compatibility with database version on startup
   - Warning/error if version mismatch detected

2. **Backward Compatibility**:
   - Migrations designed to maintain backward compatibility when possible
   - Breaking changes clearly documented and versioned
   - Multiple migration paths for complex version jumps

### Backup and Recovery

1. **Backup Strategy**:
   - Full database backups before migrations
   - Point-in-time recovery capability
   - Backup retention policy aligned with data importance

2. **Rollback Procedures**:
   - Each migration has corresponding downgrade script
   - Emergency rollback procedures documented
   - Practice drills for critical rollbacks

### Data Retention and Archiving

1. **Retention Policies**:
   - Raw LLM responses archived after 30 days
   - Completed analyses retained for 90 days
   - Aggregated results retained indefinitely

2. **Archiving Strategy**:
   - Automated archiving of old data to cold storage
   - Archive retrieval process for accessing historical data
   - Compliance with relevant data regulations

## Caching Strategy

### Overview

The application will implement a multi-level caching strategy to improve performance, reduce external API calls, and enhance user experience. The caching approach balances freshness of data with performance optimization.

### Cache Levels and Technologies

1. **Database-Level Caching**
   - Wikipedia content stored with version and timestamp
   - Analysis results stored with metadata about creation conditions
   - Implemented directly in database models with appropriate indexes

2. **Application-Level Caching**
   - In-memory cache for frequently accessed data (prompts, configurations)
   - Implemented using a simple dictionary cache with FastAPI dependency injection
   - Refreshed on application restart or explicit invalidation

3. **HTTP Response Caching**
   - Cache-Control headers for appropriate endpoints
   - ETag support for content validation
   - Vary headers to handle different authentication states

### Cache Policies by Resource Type

1. **Wikipedia Content**
   - **TTL**: 7 days
   - **Invalidation**: Manual refresh request, detection of new Wikipedia version
   - **Storage**: Database with compressed content field
   - **Key**: Wikipedia URL + version/timestamp
   - **Refresh Strategy**: Background task to periodically check for updates

2. **Analysis Results**
   - **TTL**: 3 days
   - **Invalidation**: When prompt changes or content is refreshed
   - **Storage**: Database with relationship to Wikipedia content and prompt
   - **Key**: Composite key of (page_id + page_version + prompt_id + parameters)
   - **User Control**: UI option to use cached analysis or force new analysis

3. **Prompts and Configurations**
   - **TTL**: 1 hour in application memory, permanent in database
   - **Invalidation**: Immediate on admin changes
   - **Storage**: In-memory for active use, database for persistence
   - **Refresh Strategy**: Poll database periodically for changes

4. **Admin Dashboard Statistics**
   - **TTL**: 5 minutes
   - **Storage**: In-memory with background refresh
   - **Scope**: Per-instance cache (not shared)

### Implementation Details

1. **Cache Key Design**
   - Wikipedia content: `wiki:{url}:{version}`
   - Analysis results: `analysis:{page_id}:{page_version}:{prompt_id}:{iterations}`
   - Prompts: `prompt:{prompt_id}:{last_modified}`

2. **User Experience Considerations**
   - Clear indication when viewing cached results
   - Option to request fresh analysis
   - Transparency about analysis timestamp and parameters

3. **Cache Monitoring**
   - Cache hit/miss metrics collection
   - Cache size monitoring
   - Cache efficiency reporting in admin dashboard

4. **Cache Warm-up**
   - Pre-cache popular Wikipedia pages
   - Background tasks to refresh expiring cache entries
   - Gradual cache population to avoid cold starts

### Analysis Results Caching

Analysis results caching requires special consideration to balance performance with user expectations:

1. **Composite Cache Keys**:
   - Results are cached based on the exact combination of:
     - Wikipedia page ID and version
     - Prompt ID and version
     - Analysis parameters (iterations, etc.)
   - This ensures users get consistent results for identical analyses

2. **User Choice**:
   - API supports a `use_cached` parameter (default: true)
   - When false, forces a new analysis even if cached results exist
   - Frontend presents this as an option to users

3. **Partial Result Reuse**:
   - Even for fresh analyses, the system may reuse:
     - Fetched and parsed Wikipedia content
     - Content chunking and preprocessing
   - LLM analysis is always re-run for fresh analyses

4. **Metadata and Transparency**:
   - All analysis results include:
     - When the analysis was performed
     - Which prompt version was used
     - Which Wikipedia page version was analyzed
   - This information is displayed in the UI

5. **Cache Invalidation**:
   - Cached analyses are invalidated when:
     - The prompt is updated
     - The Wikipedia page has a newer version
     - Admin manually invalidates the cache
     - TTL expires (3 days)

This approach provides performance benefits while maintaining flexibility and transparency for users.

The file structure will be as such:
   wikipedia-bias-analyzer/
   ├── app/
   │   ├── __init__.py
   │   ├── main.py
   │   ├── config.py
   │   ├── models/
   │   ├── api/
   │   ├── services/
   │   └── utils/
   ├── alembic/
   ├── tests/
   ├── requirements.txt
   └── README.md
