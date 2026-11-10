import requests
from fastapi import FastAPI, HTTPException, Query
from github_service import fetch_issues
from pydantic import BaseModel, Field


class IssueSearch(BaseModel):
    language: str
    label: str = "good first issue"
    count: int = Field(default=10, ge=1, le=50)


class IssueResponse(BaseModel):
    title: str
    repository: str
    labels: list[str]
    url: str


class IssueSearchResponse(BaseModel):
    total: int
    issues: list[IssueResponse]


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



@app.get("/issues", response_model=IssueSearchResponse)
def get_issues(
    language: str = "python",
    label: str = "good first issue",
    count: int = Query(default=10, ge=1, le=50)
):
    try:
        issues = fetch_issues(language, label, count)

    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=503,
            detail="GitHub API request timed out. Please try again."
        )

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to GitHub. Check your connection."
        )

    except requests.exceptions.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="GitHub returned an unsuccessful response."
        )

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



@app.post("/search-preview")
def search_preview(search: IssueSearch):
    return {
        "message": "Search parameters validated successfully!",
        "language": search.language,
        "label": search.label,
        "count": search.count
    }

