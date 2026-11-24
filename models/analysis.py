from enum import Enum
from pydantic import BaseModel, Field
from models.repository_analysis import RepositoryAnalysis


class Difficulty(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class DifficultyAnalysis(BaseModel):
    difficulty: Difficulty
    reason: str = Field(min_length=1)
from pydantic import BaseModel, Field


class IssueSummary(BaseModel):
    summary: str = Field(min_length=1)

class Recommendation(str, Enum):
    READY = "Ready to try"
    PREPARE = "Prepare first"
    STRETCH = "Stretch challenge"


class SuitabilityAnalysis(BaseModel):
    fit_score: int = Field(ge=0, le=100)
    suitable: bool
    matched_skills: list[str]
    missing_skills: list[str]
    recommendation: Recommendation
    reason: str = Field(min_length=1)
    preparation_skills: list[str]

class IssueAnalysis(BaseModel):
    difficulty: Difficulty
    difficulty_reason: str
    required_skills: list[str]
    summary: str
    suitability: SuitabilityAnalysis
    repository_analysis: RepositoryAnalysis | None = None