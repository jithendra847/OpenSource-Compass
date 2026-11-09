
import requests

# GitHub API endpoint
url = "https://api.github.com/search/issues"

# Search parameters
params = {
    "q": 'is:issue is:open label:"good first issue" language:python',
    "per_page": 10,
    "sort": "updated",
    "order": "desc"
}

# Request headers
headers = {
    "Accept": "application/vnd.github+json"
}

# Send GET request
response = requests.get(
    url,
    params=params,
    headers=headers,
    timeout=15
)

# Check whether request was successful
response.raise_for_status()

# Convert JSON response into Python dictionary
data = response.json()

# Extract issues
issues = data["items"]

# Display results
print("\nOPEN SOURCE PYTHON ISSUES")
print("=" * 50)

for index, issue in enumerate(issues, start=1):

    print(f"\n{index}. {issue['title']}")

    repository = issue["repository_url"].split("/repos/")[-1]

    print("Repository:", repository)

    labels = [label["name"] for label in issue["labels"]]

    print("Labels:", ", ".join(labels))

    print("URL:", issue["html_url"])

print("\nTotal issues found:", len(issues))
