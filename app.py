
import requests

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from github_service import fetch_issues
from preprocessing import recommend_issues


# --------------------------------
# 1. REQUEST MODELS
# --------------------------------

class IssueSearch(BaseModel):
    language: str
    label: str = "good first issue"
    count: int = Field(default=10, ge=1, le=50)


class RecommendationRequest(BaseModel):
    skills: list[str] = Field(min_length=1)
    language: str = "python"
    label: str | None = None
    count: int = Field(default=20, ge=1, le=50)
    min_score: int = Field(default=10, ge=0)


# --------------------------------
# 2. RESPONSE MODELS
# --------------------------------

class IssueResponse(BaseModel):
    title: str
    repository: str
    labels: list[str]
    url: str


class IssueSearchResponse(BaseModel):
    total: int
    issues: list[IssueResponse]


class RecommendationItem(BaseModel):
    id: int | None = None
    title: str
    repository: str
    labels: list[str]
    url: str
    title_matched_skills: list[str]
    body_matched_skills: list[str]
    score: int
    match_percentage: float


class RecommendationSearchResponse(BaseModel):
    total: int
    recommendations: list[RecommendationItem]


# --------------------------------
# 3. FASTAPI APPLICATION
# --------------------------------

app = FastAPI(
    title="OpenSource Compass API",
    description="Discover beginner-friendly open-source issues",
    version="0.1.0"
)


# --------------------------------
# 4. HOME ENDPOINT
# --------------------------------

@app.get("/")
def home():
    return {
        "message": "Welcome to OpenSource Compass API!",
        "status": "running"
    }


# --------------------------------
# 5. GITHUB ISSUE SEARCH
# --------------------------------

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

        labels = [
            item["name"]
            for item in issue["labels"]
        ]

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


# --------------------------------
# 6. SEARCH PREVIEW
# --------------------------------

@app.post("/search-preview")
def search_preview(search: IssueSearch):

    return {
        "message": "Search parameters validated successfully!",
        "language": search.language,
        "label": search.label,
        "count": search.count
    }


# --------------------------------
# 7. ISSUE RECOMMENDATION ENGINE
# --------------------------------

@app.post(
    "/recommendations",
    response_model=RecommendationSearchResponse
)
def get_recommendations(request: RecommendationRequest):

    try:

        # Fetch real GitHub issues
        issues = fetch_issues(
            request.language,
            request.label,
            request.count
        )

        # Pass fetched issues to our recommendation engine
        recommendations = recommend_issues(
            request.skills,
            issues,
            request.min_score
        )

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

    # Prepare API response
    results = []

    for issue in recommendations:

        repository_url = issue.get("repository_url") or ""

        repository = (
            repository_url.rsplit("/repos/")[-1] 
            if repository_url else ""
        )

        results.append({
            "id": issue["id"],
            "title": issue["title"],
            "repository": repository,
            "labels": issue["labels"],
            "url": issue["url"],
            "title_matched_skills": issue["title_matched_skills"],
            "body_matched_skills": issue["body_matched_skills"],
            "score": issue["score"],
            "match_percentage": issue["match_percentage"],
        })

    return {
        "total": len(results),
        "recommendations": results
    }
