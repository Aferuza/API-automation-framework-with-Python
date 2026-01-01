# Import pytest for testing framework features like fixtures and parametrization
import pytest
from user_api_interctions import create_user, get_user, delete_user
# Importing API interaction functions (create, get, delete user)
from utils import retry_request, validate_response, get_jwt_token

# Importing custom utility functions for retry logic and response validation
from utils import retry_request, validate_response


# -------------------- FIXTURES --------------------

@pytest.fixture
def sample_user():
    """Fixture that provides reusable test data for user creation.
    Useful when multiple tests need the same input.
    """
    return {
        "name": "John Doe",
        "job": "QA Engineer"
    }


# -------------------- TEST CASES --------------------

def test_create_user(sample_user):
    """
    ✅ Test: Verify that creating a new user works successfully.
    - Sends POST request with user data.
    - Asserts HTTP 201 Created status.
    - Checks that the name in the response matches input.
    """
    response = create_user(sample_user)
    assert response.status_code == 201, "Expected 201 Created"
    data = response.json()
    assert data['name'] == sample_user['name'], "User name mismatch in response"


def test_get_user_success():
    """
    Test: Verify fetching an existing user by ID.
    - Uses retry logic to handle temporary API delays or network issues.
    - Confirms correct status code and user ID in response.
    """
    # Retry logic: keep retrying `get_user(2)` until success or timeout
    response = retry_request(lambda: get_user(2))
    assert response.status_code == 200, "Expected 200 OK"
    assert response.json()['data']['id'] == 2, "Fetched wrong user ID"


@pytest.mark.parametrize("user_id, validator", [
    # Positive case: existing user should return 200 and contain 'data' key
    (2, lambda r: r.status_code == 200 and "data" in r.json()),

    # Negative case: non-existent user should return 404
    (999, lambda r: r.status_code == 404),
])
def test_get_user_validation(user_id, validator):
    """
    Test: Parameterized validation for multiple user IDs.
    - Runs test twice: for valid (2) and invalid (999) user IDs.
    - Uses custom validator functions to check response logic dynamically.
    """
# -------------------- FIXTURES --------------------

@pytest.fixture(scope="session")
def auth_headers():
    """
    Fixture to generate and reuse a JWT Bearer token for all tests in a session.
    In real scenarios, this can call an auth endpoint to fetch a fresh token.
    """
    token = get_jwt_token()  # Your custom util that returns a valid JWT
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_user():
    """Reusable user data for creating a new user."""
    return {
        "name": "John Doe",
        "job": "QA Engineer"
    }


# -------------------- TEST CASES --------------------

def test_create_user(sample_user, auth_headers):
    """Test user creation with authentication."""
    response = create_user(sample_user, headers=auth_headers)
    assert response.status_code == 201, "Expected 201 Created"
    data = response.json()
    assert data['name'] == sample_user['name']


def test_get_user_success(auth_headers):
    """Test fetching a user with valid JWT authentication."""
    response = retry_request(lambda: get_user(2, headers=auth_headers))
    assert response.status_code == 200
    assert response.json()['data']['id'] == 2


@pytest.mark.parametrize("user_id, validator", [
    (2, lambda r: r.status_code == 200 and "data" in r.json()),
    (999, lambda r: r.status_code == 404),
])
def test_get_user_validation(user_id, validator, auth_headers):
    """Parametrized validation using dynamic lambda-based validators."""
    response = get_user(user_id, headers=auth_headers)
    assert validate_response(response, validator)


def test_delete_user(auth_headers):
    """Test deleting a user with JWT authentication."""
    response = delete_user(2, headers=auth_headers)
    assert response.status_code == 204