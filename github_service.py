
import requests


def fetch_issues(language, label, count):

    url = "https://api.github.com/search/issues"

    # Base query: fetch all open issues for the language
    query = f"is:issue is:open language:{language}"

    # Apply a label filter only when one is provided
    if label:
        query += f' label:"{label}"'

    params = {
        "q": query,
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

    print("\nGITHUB API RATE LIMIT")
    print("Limit:", response.headers.get("X-RateLimit-Limit"))
    print("Remaining:", response.headers.get("X-RateLimit-Remaining"))
    print("Reset:", response.headers.get("X-RateLimit-Reset"))

    data = response.json()

    return data["items"]
