
import requests


def fetch_issues(language, label, count):

    url = "https://api.github.com/search/issues"

    params = {
        "q": f'is:issue is:open label:"{label}" language:{language}',
        "per_page": count,
        "sort": "updated",
        "order": "desc"
    }

    headers = {
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    return data["items"]


# Fetch Python issues
issues = fetch_issues("python", "good first issue", 10)


# Display results
for index, issue in enumerate(issues, start=1):

    repository = issue["repository_url"].split("/repos/")[-1]

    labels = [label["name"] for label in issue["labels"]]

    print(f"\n{index}. {issue['title']}")
    print("Repository:", repository)
    print("Labels:", ", ".join(labels))
    print("URL:", issue["html_url"])

print("\nTotal issues:", len(issues))
