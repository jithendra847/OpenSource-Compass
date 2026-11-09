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

    try:
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

    except requests.exceptions.Timeout:
        print("Request timed out. Please try again.")
        return []

    except requests.exceptions.ConnectionError:
        print("Check your internet connection.")
        return []

    except requests.exceptions.HTTPError as error:
        print("GitHub API error:", error)
        return []

    except requests.exceptions.RequestException as error:
        print("Request failed:", error)
        return []
