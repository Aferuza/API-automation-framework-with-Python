from jinja2 import Template
from pathlib import Path

# Simple HTML template for test report
HTML_TEMPLATE = """
<html>
<head><title>API Test Report</title></head>
<body>
<h1>API Test Results</h1>
<p>Status: {{ status }}</p>
<p>Response Time: {{ time }}</p>
</body>
</html>
"""

# Generate HTML report from test results
def generate_report(status, time):
    template = Template(HTML_TEMPLATE)

    # Render template with dynamic values
    html = template.render(status=status, time=time)

    # Ensure results directory exists
    Path("results").mkdir(exist_ok=True)

    # Write report to file
    with open("results/report.html", "w") as f:
        f.write(html)

# FIX: Pass arguments to the function call
# In a real scenario, these values would come from your test execution logic
if __name__ == "__main__":
    generate_report("Passed", "120ms")

