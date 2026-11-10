from fastapi import FastAPI
from github_service import fetch_issues

app = FastAPI(
    title="OpenSource Compass API",
    description="Discover beginner-friendly open-source issues",
    version="0.1.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to OpenSource Compass API!",
        "status": "running"
    }


@app.get("/issues")
def get_issues(
    language: str = "python",
    label: str = "good first issue",
    count: int = 10
):
    issues = fetch_issues(language, label, count)

    results = []

    for issue in issues:
        repository = issue["repository_url"].split("/repos/")[-1]

        labels = [item["name"] for item in issue["labels"]]

        results.append({
            "title": issue["title"],
            "repository": repository,
            "labels": labels,
            "url": issue["html_url"]
        })

    return {
        "total": len(results),
        "issues": results
    }

@app.get("/hello/{username}")
def say_hello(username: str):
    return {
        "message": f"Hello, {username}!"
    }