
# API Test Automation Framework using GitHub REST API - based on Python/Pytest

This project is a Python-based API automation framework that could display how QA and DevOps teams build scalable,
 maintainable, and CI/CD-ready automated testing solutions for backend systems.
It validates GitHub REST APIs (uses live APIs rather than mocks) with focus on backend quality, API contracts, authentication, performance,
and DevOps practices.

## What Is Validated in this Framework:
* API authentication and authorization (OAuth2 Bearer Token)
* CRUD operations on GitHub resources
* HTTP response status codes
* API response structure using JSON Schema
* API performance and response time
* Backend behavior consistency across requests

## Key Objectives:
* Validate backend correctness, contracts, and performance in a single execution
* Provide clean and reusable abstractions for HTTP interactions
* Enable safe automation against live APIs
* Align QA automation with CI/CD and DevOps workflows

## Tech Stack:
* Language: Python 3
* Testing Framework: Pytest
* HTTP Client: Requests
* Schema Validation: jsonschema
* Configuration Management: python-dotenv
* Authentication: OAuth2 Bearer Token
* Reporting: HTML reports (pytest-html / Jinja2 ready)


## Project Structure
api-automation-framework/
├── requirements.txt
├── .env
├── run_tests.py
├── src/
│   ├── api/
│   │   ├── api_client.py        # Generic HTTP client (GET/POST/PATCH/DELETE)
│   │   └── endpoints.py         # Centralized GitHub API endpoints
│   ├── auth/
│   │   └── auth_client.py       # Authentication handling
│   ├── utils/
│   │   ├── config.py            # Environment configuration
│   │   └── logger.py            # Centralized logging
│   ├── validation/
│   │   ├── schema_validator.py  # JSON schema validation
│   │   └── schemas/
│   │       └── user_schema.json
│   └── reporting/
│       └── report_generator.py  # HTML report generation
├── tests/
│   └── test_users_api.py        # Pytest-based API tests
└── results/
    └── report.html

## Framework Design Principles:
### 1.API Client Abstraction
All HTTP logic is encapsulated in a reusable API client layer.
This prevents duplicated request code, centralizes authentication handling, and keeps test cases clean and readable.

### 2.Endpoint Centralization
All API paths are defined in a single endpoints module, for example:
* /user
* /user/repos
* /repos/{owner}/{repo}
This avoids hardcoded URLs, makes refactoring safe, and mirrors real microservice test design.

### 3.Authentication and Security
* OAuth2 Bearer Token authentication
* Secrets injected via environment variables
* No credentials are hardcoded or committed to the repository

### 4.Schema Validation (Contract Testing)
JSON Schema validation is used to:
* Detect breaking API changes
* Enforce response structure
* Protect downstream services that depend on the API

### 5.Performance Validation
Each API request captures response time and validates it against a defined threshold.
This allows early detection of backend performance regressions.

## 6.Test Coverage
### Authenticated User Validation
* OAuth token validation
* Access scope verification
* Schema validation of the /user endpoint

### 7.Repository Lifecycle Test:
A full backend lifecycle scenario is automated:
1. Create repository
   POST /user/repos

2. Read repository metadata
   GET /repos/{owner}/{repo}

3. Update repository settings
   PATCH /repos/{owner}/{repo}

4. Delete repository
   DELETE /repos/{owner}/{repo}

Each step validates:
* HTTP status codes
* Response payload correctness
* API behavior consistency

## Setup
1. Clone the repository
2. Create a .env file in the project root
3. Add your GitHub configuration:
GITHUB_BASE_URL=https://api.github.com
GITHUB_TOKEN=your_personal_access_token

## Running the Tests
Run all tests:
pytest -v

Run a specific test file:
pytest tests/test_users_api.py

Generate HTML report:
pytest --html=results/report.html

Open the report:
results/report.html

## Planned Enhancements to this framework:
* GitHub Actions CI workflow
* Retry and rate-limit handling
* OAuth token lifecycle testing
* Parallel test execution
* Enhanced logging and reporting
* Mock API support using responses or httpretty

This framework is designed to run in:
* GitHub Actions
* Docker containers
* Headless CI pipelines

## Why I chose GitHub API vs mock services?:
GitHub API provides:
* Real authentication flows
* Real authorization scopes
* Real rate limits
* Production-grade backend behavior

