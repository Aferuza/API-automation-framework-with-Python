import requests  # ✅ Used to send HTTP requests (GET, POST, etc.)

# 🌐 Base URL of the public mock API (ReqRes)
# This acts as our target endpoint for API testing.
BASE_URL = "https://reqres.in/api"

# ---------------------------------------------------------
def test_get_single_user():
    """
    🔍 Test Case: Validate fetching a single user's data
    Objective:
        - Send a GET request to retrieve user with ID=2
        - Verify that:
            1. Response status code is 200 (OK)
            2. The returned user's ID matches 2
    """
    # Send GET request to retrieve a single user
    response = requests.get(f"{BASE_URL}/users/2")

    # ✅ Verify the API responded successfully
    assert response.status_code == 200, "Expected 200 OK response"

    # ✅ Parse JSON response and validate 'id' field
    data = response.json()
    assert data['data']['id'] == 2, "User ID should be 2"


# ---------------------------------------------------------
def test_create_user():
    """
    🧩 Test Case: Validate user creation functionality
    Objective:
        - Send a POST request with name and job details
        - Verify that:
            1. Response status code is 201 (Created)
            2. The response body echoes the correct name field
    """
    # Request payload (data we send in the body)
    payload = {
        "name": "Feruza",
        "job": "QA Engineer"
    }

    # Send POST request to create a new user
    response = requests.post(f"{BASE_URL}/users", json=payload)

    # ✅ Validate the correct HTTP status code
    assert response.status_code == 201, "Expected 201 Created"

    # ✅ Validate the name in response matches the sent payload
    response_data = response.json()
    assert response_data['name'] == "Feruza", "Expected name 'Feruza' in response"

