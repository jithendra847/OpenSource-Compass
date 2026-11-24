
from pydantic import BaseModel, Field


class RelevantFile(BaseModel):
    path: str
    purpose: str
    evidence: str


class ImplementationStep(BaseModel):
    step: int
    file_path: str | None = None
    instruction: str
    reason: str


class RepositoryAnalysis(BaseModel):
    repository_summary: str
    issue_interpretation: str

    relevant_files: list[RelevantFile]

    investigation_notes: list[str]

    implementation_steps: list[ImplementationStep]

    testing_strategy: list[str]

    uncertainty_notes: list[str]
