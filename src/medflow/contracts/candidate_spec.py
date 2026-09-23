from typing import Any, Literal

from pydantic import BaseModel, Field


# ==========================================
# Dataset
# ==========================================

class CandidateDataset(BaseModel):
    name: str | None = None
    version: str | None = None
    local_path: str | None = None


# ==========================================
# Population
# ==========================================

class CandidatePopulation(BaseModel):
    description: str | None = None
    age_min: float | None = None
    age_max: float | None = None


# ==========================================
# Exposure
# ==========================================

class CandidateExposure(BaseModel):
    name: str | None = None
    column: str | None = None

    data_type: Literal[
        "continuous",
        "categorical",
        "binary",
    ] | None = None

    unit: str | None = None

    analysis_form: Literal[
        "continuous",
        "categorical",
    ] | None = None


# ==========================================
# Outcome
# ==========================================

class CandidateBinaryCoding(BaseModel):
    negative_value: Any | None = None
    positive_value: Any | None = None


class CandidateOutcome(BaseModel):
    name: str | None = None
    column: str | None = None

    data_type: Literal[
        "binary",
    ] | None = None

    coding: CandidateBinaryCoding | None = Field(
        default_factory=CandidateBinaryCoding
    )

    definition: str | None = None


# ==========================================
# Covariate
# ==========================================

class CandidateCovariate(BaseModel):
    name: str

    column: str | None = None

    data_type: Literal[
        "continuous",
        "categorical",
        "binary",
    ] | None = None

    unit: str | None = None

    reference_value: Any | None = None


# ==========================================
# Missing Data
# ==========================================

class CandidateMissingData(BaseModel):
    strategy: Literal[
        "complete_case_global",
    ] | None = None


# ==========================================
# Analysis
# ==========================================

class CandidateAnalysis(BaseModel):
    """
    当前 V0.1 只支持 Logistic Regression。

    注意：
    如果用户没有明确提出统计方法，
    LLM 不允许自行推断，应保持 None，
    后续由科研人员人工确认。
    """

    method: Literal[
        "logistic_regression",
    ] | None = None


# ==========================================
# Open Issue
# ==========================================

class OpenIssue(BaseModel):
    issue_id: str
    field_path: str

    issue_type: Literal[
        "missing",
        "ambiguous",
        "unsupported",
        "conflict",
    ]

    blocking: bool = True

    question: str


# ==========================================
# Candidate Research Spec V0.1
# ==========================================

class CandidateResearchSpecV01(BaseModel):

    schema_version: Literal[
        "0.1.0"
    ] = "0.1.0"

    source_question: str

    study_design: Literal[
        "cross_sectional"
    ] | None = None

    objective: Literal[
        "association"
    ] | None = None

    dataset: CandidateDataset = Field(
        default_factory=CandidateDataset
    )

    population: CandidatePopulation = Field(
        default_factory=CandidatePopulation
    )

    exposure: CandidateExposure = Field(
        default_factory=CandidateExposure
    )

    outcome: CandidateOutcome = Field(
        default_factory=CandidateOutcome
    )

    covariates: list[
        CandidateCovariate
    ] = Field(
        default_factory=list
    )

    missing_data: CandidateMissingData = Field(
        default_factory=CandidateMissingData
    )

    analysis: CandidateAnalysis = Field(
        default_factory=CandidateAnalysis
    )

    open_issues: list[
        OpenIssue
    ] = Field(
        default_factory=list
    )