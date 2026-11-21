from enum import Enum
from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class DifficultyAnalysis(BaseModel):
    difficulty: Difficulty
    reason: str = Field(min_length=1)
