# Python API Automation Framework (QA / DevOps Portfolio)

This project is a Python-based API automation framework designed to demonstrate how QA and DevOps teams build
scalable, maintainable, and CI/CD-ready automated testing solutions in real-world environments.

The framework focuses on API testing best practices, including authentication handling, schema validation,
performance checks, logging, and report generation.


##                                             Key Features

- Secure API authentication using environment variables
- Modular API client abstraction
- JSON schema validation for contract testing
- Response time performance validation
- Centralized logging
- HTML report generation
- CI/CD-friendly design
- Clean, scalable project structure



##                                            Tech Stack

- **Language:** Python
- **Testing Framework:** Pytest
- **HTTP Client:** Requests
- **Schema Validation:** jsonschema
- **Configuration Management:** python-dotenv
- **Reporting:** Jinja2 (HTML)
- **CI/CD Ready:** Yes (Docker / GitHub Actions compatible)


#                                           Project Structure
# API Test Automation Project

This project contains automated API tests for a mock backend using Python,
pytest, and requests.

##                                          Features
- Covers GET and POST endpoints
- Validates status codes and response bodies
- Generates HTML reports
What Is Validated

API authentication

HTTP response status codes

API response structure (JSON Schema)

API performance (response time)

Logging and traceability


##                                         Setup

1. Clone the repository
2. Create a .env file in the project root
3. Add your GitHub token:

`env
GITHUB_BASE_URL=https://api.github.com
GITHUB_TOKEN=your_personal_access_token

## How to Run
1. Clone repo
2. Install requirements: `pip install -r requirements.txt`
3. Run tests: `pytest --html=report.html`
4. View report

Open:
results/report.html




                                            Further enhancement the proj:
- Add **logging**
- Generate test reports with `pytest-html`
- Integrate with a CI tool (GitHub Actions or GitLab CI)
- Mock APIs using `responses` or `httpretty`



api-automation-framework/
├── requirements.txt
├── .env
├── run_tests.py
├── src/
│ ├── api/
│ │ ├── api_client.py
│ │ └── endpoints.py
│ ├── auth/
│ │ └── auth_client.py
│ ├── utils/
│ │ ├── config.py
│ │ └── logger.py
│ ├── validation/
│ │ ├── schema_validator.py
│ │ └── schemas/
│ │ └── user_schema.json
│ └── reporting/
│ └── report_generator.py
├── tests/
│ └── test_users_api.py
└── results/
└── report.html
