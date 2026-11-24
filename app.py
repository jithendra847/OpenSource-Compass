
import requests

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field

from github_service import fetch_issues
from recommendation_engine import recommend_issues

from ai.issue_analyzer import analyze_issue
from models.analysis import IssueAnalysis

from ai.recommendation_service import enrich_recommendations

from ai.repository_context import fetch_repository_context
from ai.repository_analyzer import analyze_repository_issue

from ai.llm_client import LLMAPIError
# --------------------------------
# 1. REQUEST MODELS
# --------------------------------

class IssueSearch(BaseModel):
    """Parameters used to validate a GitHub issue search."""

    language: str = Field(
        description="Programming language of the repositories to search."
    )
    label: str = Field(
        default="good first issue",
        description="GitHub issue label used to filter results."
    )
    count: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Number of issues to request (1-50)."
    )


class RecommendationRequest(BaseModel):
    """Parameters for personalized issue recommendations."""

    skills: list[str] = Field(
        min_length=1,
        description="Programming languages and technologies the developer knows."
    )
    language: str = Field(
        default="python",
        min_length=1,
        description="Programming language used to filter repositories."
    )
    label: str | None = Field(
        default=None,
        description="Optional GitHub issue label filter."
    )
    count: int = Field(
        default=20,
        ge=1,
        le=50,
        description="Number of GitHub issues to analyze (1-50)."
    )
    min_score: int = Field(
        default=10,
        ge=0,
        description="Minimum recommendation score required for an issue."
    )


class IssueAnalysisRequest(BaseModel):
    """Parameters required to analyze an open-source issue."""

    title: str = Field(
        min_length=1,
        description="Title of the GitHub issue."
    )
    body: str = Field(
        default="",
        description="Description of the GitHub issue."
    )
    labels: list[str] = Field(
        default_factory=list,
        description="Labels attached to the GitHub issue."
    )
    user_skills: list[str] = Field(
        default_factory=list,
        description="Programming skills known by the developer."
    )
    repository: str | None = Field(
    default=None,
    description="GitHub repository in owner/name format."
    ) 
    issue_number: int | None = Field(
    default=None,
    gt=0,
    description="GitHub issue number."
    )

# --------------------------------
# 2. RESPONSE MODELS
# --------------------------------

class IssueResponse(BaseModel):
    """A simplified GitHub issue returned by the API."""

    title: str
    repository: str
    labels: list[str]
    url: str


class IssueSearchResponse(BaseModel):
    """Response containing the total number of issues and issue results."""

    total: int
    issues: list[IssueResponse]


class RecommendationItem(BaseModel):
    """An issue ranked by skill relevance and AI analysis."""

    id: int | None = None
    issue_number: int | None = None
    repository_url: str | None = None
    title: str
    repository: str
    labels: list[str]
    url: str
    title_matched_skills: list[str]
    body_matched_skills: list[str]
    score: int
    match_percentage: float
    explanation: list[str]

    hybrid_score: float | None = None
    analysis: IssueAnalysis | None = None
    analysis_status: str


class RecommendationSearchResponse(BaseModel):
    """Response containing personalized issue recommendations."""

    total: int
    recommendations: list[RecommendationItem]


# --------------------------------
# 3. FASTAPI APPLICATION
# --------------------------------

app = FastAPI(
    title="OpenSource Compass API",
    description="""
# OpenSource Compass

Discover beginner-friendly open-source issues and find contributions
that match your programming skills.

## Features
- Search GitHub issues by programming language and label.
- Receive skill-based issue recommendations.
- See matched skills, recommendation scores, and explanations.
- Validate search parameters before making requests.

## How to use
1. Search for issues using `/issues`.
2. Submit your skills using `/recommendations`.
3. Review scores and explanations to choose issues.

GitHub is the external data source for issue discovery.
""",
    version="0.1.0",
    openapi_tags=[
        {
            "name": "General",
            "description": "General API information and status."
        },
        {
            "name": "Issues",
            "description": "Search and validate GitHub issue discovery parameters."
        },
        {
            "name": "Recommendations",
            "description": "Find open-source issues based on developer skills."
        }
    ]
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------
# 4. HOME ENDPOINT
# --------------------------------

@app.get(
    "/",
    tags=["General"],
    summary="API health check",
    description="Check whether OpenSource Compass API is running.",
    responses={
        200: {"description": "API is running successfully."}
    }
)
def home():
    return {
        "message": "Welcome to OpenSource Compass API!",
        "status": "running"
    }


# --------------------------------
# 5. GITHUB ISSUE SEARCH
# --------------------------------

@app.get(
    "/issues",
    response_model=IssueSearchResponse,
    tags=["Issues"],
    summary="Search GitHub issues",
    description="""
Fetch open GitHub issues using a programming language and issue label.

The results include issue titles, repository names, labels, and GitHub URLs.
""",
    responses={
        200: {"description": "Issues retrieved successfully."},
        422: {"description": "Invalid search parameters."},
        502: {"description": "GitHub returned an unsuccessful response."},
        503: {"description": "GitHub timed out or could not be reached."}
    }
)
def get_issues(
    language: str = Query(
        default="python",
        min_length=1,
        description="Programming language used to filter repositories."
    ),
    label: str = Query(
        default="good first issue",
        description="GitHub issue label to search for."
    ),
    count: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Number of issues to retrieve (1-50)."
    )
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

    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=502,
            detail="GitHub request failed. Please try again."
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

@app.post(
    "/search-preview",
    tags=["Issues"],
    summary="Preview validated search parameters",
    description="""
Validate issue search parameters without making a GitHub API request.

Useful for checking the language, label, and result count before searching.
""",
    responses={
        200: {"description": "Search parameters validated successfully."},
        422: {"description": "Invalid request body or parameter values."}
    }
)
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
    response_model=RecommendationSearchResponse,
    tags=["Recommendations"],
    summary="Recommend issues based on developer skills",
    description="""
Find open-source issues that match the developer's skills.

Issues are fetched from GitHub and processed by the recommendation engine.
Matching skills, relevance scores, match percentages, and explanations
are returned to help developers decide which issues to work on.

### Recommendation parameters
- **skills:** Skills you know, such as Python, JavaScript, or C++.
- **language:** Repository programming language filter.
- **label:** Optional issue label filter.
- **count:** Number of issues to analyze (1-50).
- **min_score:** Minimum score required for an issue to be recommended.
""",
    responses={
        200: {"description": "Recommendations generated successfully."},
        422: {"description": "Invalid request body or parameter values."},
        502: {"description": "GitHub returned an unsuccessful response."},
        503: {"description": "GitHub timed out or could not be reached."}
    }
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

    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=502,
            detail="GitHub request failed. Please try again."
        )
    recommendations = enrich_recommendations(
                recommendations,
                request.skills,
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
            "issue_number": issue.get("issue_number"),
            "repository_url": repository_url,
            "title": issue["title"],
            "repository": repository,
            "labels": issue["labels"],
            "url": issue["url"],
            "title_matched_skills": issue["title_matched_skills"],
            "body_matched_skills": issue["body_matched_skills"],
            "score": issue["score"],
            "match_percentage": issue["match_percentage"],
            "explanation": issue["explanation"],
            "hybrid_score": issue["hybrid_score"],
            "analysis": issue["analysis"],
            "analysis_status": issue["analysis_status"],
            
        })

    return {
        "total": len(results),
        "recommendations": results
    }


# --------------------------------
# 8. AI ISSUE ANALYSIS
# --------------------------------

@app.post(
    "/analyze-issue",
    response_model=IssueAnalysis,
    tags=["Analysis"],
    summary="Analyze an open-source issue",
    description="""
    Analyze an issue's difficulty, required skills,
    summary, and suitability and optionally its source code.
    """
)
def analyze_github_issue(request: IssueAnalysisRequest):

    # Run the existing issue analysis first.
    result = analyze_issue(
        title=request.title,
        body=request.body,
        labels=request.labels,
        user_skills=request.user_skills,
    )

    # Repository analysis is optional.
    if not request.repository:
        return result

    if not request.issue_number:
        raise HTTPException(
            status_code=422,
            detail="issue_number is required when repository is provided.",
        )

    # Validate repository format: owner/repository
    parts = request.repository.split("/")

    if len(parts) != 2 or not all(parts):
        raise HTTPException(
            status_code=422,
            detail="Repository must use the format 'owner/repository'.",
        )

    owner, repo = parts

    try:
        # Retrieve relevant source code from GitHub.
        repository_context = fetch_repository_context(
            owner=owner,
            repo=repo,
            issue_title=request.title,
            issue_body=request.body,
        )

        # Generate the detailed contribution guide.
        repository_result = analyze_repository_issue(
            title=request.title,
            body=request.body,
            labels=request.labels,
            user_skills=request.user_skills,
            repository_context=repository_context,
        )

        result.repository_analysis = repository_result

    except requests.RequestException as error:
        raise HTTPException(
            status_code=502,
            detail=f"Could not retrieve repository information from GitHub: {error}",
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    except LLMAPIError as error:
        raise HTTPException(
            status_code=503,
            detail=(
                "AI analysis is temporarily unavailable because "
                "the model provider has reached its usage limit. "
                "Please try again later."
            ),
        ) from error

    return result