from src.api.api_client import APIClient
from src.api.endpoints import REPO,USER
from src.utils.config import API_BASE_URL, AUTH_TOKEN, GITHUB_USERNAME, GITHUB_REPO

client = APIClient(base_url=API_BASE_URL, token=AUTH_TOKEN)

'''response
│
├── status_code → 200
│
├── json
│      │
│      ├── login
│      ├── id
│      ├── company
│      ├── bio
│      ├── location
│      └── ...
│
├── headers
│      │
│      ├── Date
│      ├── Content-Type
│      ├── Server
│      └── ...
│
└── response_time → 1.04'''

# 1. Inspect the full response dict structure
response = client.get(USER)
print("====Top level keys===")
print(list(response.keys())) #['status_code', 'json', 'headers', 'response_time']
print("====Top level values===")

# response dict has nested dicts in it: json, headers, etc
print(list(response.values())) #there are nested values, nested  lists-
# 1st value- 200, 2nd value- is a dict (key is json(body)
print(len(response["json"])) #34
# because the headers dictionary contains around 25 header fields.
print(len(response["headers"]))#26


# 1.1. To print the key value pairs in a nice way on each line
print("Print each k:v on a single line")
body = response["json"]

for key, value in body.items():
    print(f"{key}: {value}")
'''login: Aferuza
id: 45316760
node_id: MDQ6VXNlcjQ1MzE2NzYw
avatar_url: https://avatars.githubusercontent.com/u/45316760?v=4
gravatar_id: '''


# 2. Inspect the json body
print("\n===JSON BODY KEYS===")
# Because iterating over a dictionary automatically iterates over its keys.
print(list(response["json"]))# output same as below
# keys() returns the dictionary's keys.
print(list(response["json"].keys())) # output same as above

# 3. To find nested structures
print("Nested structures")
# the body of response is the json var
body=response["json"]
for key,value in body.items():
    print(f"{key}:{type(value).__name__}={repr(value)[:60]}")
'''This code snippet is a highly effective **debugging utility for inspecting the structure and data types** of a JSON response.

When you run this, it will iterate through the top-level keys of your JSON object and print a formatted summary of each key, the type of data associated with it, 
and a truncated preview of the actual value.

### What it Produces (Example)

Assuming `response["json"]` contains data from a typical API call, the output would look like this in your console:

```text
id:int=1024
username:str='qa_engineer_pro'
is_active:bool=True
roles:list=['admin', 'tester', 'viewer']
metadata:dict={'created_at': '2026-06-01', 'last_login': '2026-07-10'}
config:NoneType=None

```

---

### Breakdown of the Logic

1. **`body = response["json"]`**: This extracts the dictionary (or list of dicts) from the `response` object.
2. **`for key, value in body.items():`**: This loops through every key-value pair in that dictionary.
3. **`f"{key}:"`**: Prints the name of the field (the key).
4. **`{type(value).__name__}=`**: This uses Python's `type()` function to dynamically show you if the data is a `str`, `int`, `list`, `dict`, `bool`, etc. This is incredibly useful for spotting bugs (e.g., discovering an ID is coming back as a `str` when you expected an `int`).
5. **`{repr(value)[:60]}`**:
* **`repr(value)`**: Returns a string representation of the object (often including quotes for strings).
* **`[:60]`**: **This is the safety valve.** If a key contains a massive string (like a full base64 image or a massive log), this slice prevents your terminal from being flooded with thousands of lines of text by cutting the output at 60 characters.



### Why this is useful for your QA workflow

* **Quick Schema Verification:** You can visually confirm if the API is returning the types you defined in your JSON Schema.
* **Troubleshooting Payload Errors:** If a test fails because of a `TypeMismatch`, you can run this to immediately see if a field that *should* be a number is being passed as a string.
* **Exploratory Testing:** When testing a new API endpoint, it gives you a clean "bird's-eye view" of what the response structure actually looks like without having to print the entire raw blob.

**Pro-tip:** If you find yourself doing this often, consider wrapping this logic into a small helper method in your test framework so you can call `inspect_response(response)` whenever a test fails!'''



# 4. Safely extract values
# At the moment you execute that code, they are the exact same thing.
# Memory Reference: body is simply a variable name pointing to the exact same Python object (the dictionary) that response["json"] references.
print("Safe access")
print(body.get("login"))#Aferuza
print(body.get("unexpected"))#None
print(body)
'''print(response["json"]): This tells someone reading your code where the data is coming from (the response object).

print(body): This tells someone what the data represents (the body of the response). 
It is cleaner and easier to read, especially if you are using the body variable in multiple places (assertions, logging, debugging).
Error Handling (The "QA" Advantage)
If you are writing a robust framework, you rarely want to access response["json"] directly multiple times. If response happens to be None or missing the "json" key, your code will crash.

Using a variable allows you to do this:
# Safer pattern
body = response.get("json")

# if body is empty and we got 204 No Content status code
if body is not None:
    print(body)
    # Perform your type checks here
else:
    print("Error: No JSON body found in response!")'''

# 5 Inspect headers dict
print("Rate limit headers")
headers = response["headers"]
rate_limit_keys = [k for k in headers if "rate" in k.lower()]
for k in rate_limit_keys:
    print(f"{k}:{headers[k]}")

#     X-RateLimit-Limit:5000
# X-RateLimit-Remaining:4928
# X-RateLimit-Reset:1783739889
# X-RateLimit-Used:72
# X-RateLimit-Resource:core

'''The goal of this code snippet is to verify that the API’s rate-limiting mechanism is active and configured correctly without having to manually sift through every single header returned by the server.

As a QA Automation Engineer, this is a proactive "health check" for the API's traffic management.

Why this specific logic matters:
Ensuring Compliance with Service Level Agreements (SLAs): Most APIs have rate limits (e.g., "1,000 requests per hour"). By printing these headers, you can confirm that the server is communicating its limits to the client.

Debugging 429 Errors: If your automated tests suddenly start failing with 429 Too Many Requests errors, this snippet allows you to quickly see the current state of your "budget" (e.g., X-RateLimit-Remaining: 0) without needing to inspect the full raw headers object.

Dynamic Key Discovery: APIs often use different naming conventions for rate limits (e.g., X-RateLimit-Limit, RateLimit-Limit, X-Rate-Limit-Remaining). Because the code uses if "rate" in k.lower(), it is "future-proof"—it will catch the relevant headers even if the API provider changes their naming convention slightly.

What the Output Tells You
When you run this, you are effectively creating a "Rate Limit Dashboard" for your test logs:

X-RateLimit-Limit: The maximum number of requests you are allowed to make in a window.

X-RateLimit-Remaining: How many requests you have left before you get throttled.

X-RateLimit-Reset: A timestamp indicating when your quota will reset.

Pro-Tip for your QA Framework
If you are building an automated framework, you can turn this "inspect" logic into a "Validator":

Python
def validate_rate_limit(headers):
    # Instead of just printing, assert that the limit exists
    assert any("rate" in k.lower() for k in headers), "Rate limit headers missing!"
    
    # Or, verify you aren't about to be throttled
    remaining = int(headers.get("X-RateLimit-Remaining", 1))
    if remaining < 10:
        print(f"WARNING: Low rate limit remaining: {remaining}")
Does your current API under test have strict rate limits that often cause your tests to flake or fail during execution?'''





# july 12:
# 


