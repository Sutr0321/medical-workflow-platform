from typing import Any

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

    # Research Planning 层允许记录研究者实际选择的变量类型。
    # 是否能被当前执行引擎支持，由后续 Capability Check 判断。
    data_type: str | None = None

    # 当前阶段只是“计划报告单位”，
    # 真实数据源单位必须在 Data Binding 阶段核对。
    unit: str | None = None

    analysis_form: str | None = None


# ==========================================
# Outcome
# ==========================================

class CandidateBinaryCoding(BaseModel):
    negative_value: Any | None = None
    positive_value: Any | None = None


class CandidateOutcome(BaseModel):
    name: str | None = None
    column: str | None = None

    # 不再把 Research Plan 限死为 binary。
    # binary / continuous / time_to_event / count 等
    # 都可以在规划层记录。
    data_type: str | None = None

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

    data_type: str | None = None

    unit: str | None = None

    reference_value: Any | None = None


# ==========================================
# Missing Data
# ==========================================

class CandidateMissingData(BaseModel):
    """
    Research Planning 层记录科研人员真正选择的缺失值策略。

    例如：
    complete_case_global
    multiple_imputation

    当前执行引擎是否支持，不在这里限制。
    """

    strategy: str | None = None


# ==========================================
# Analysis
# ==========================================

class CandidateAnalysis(BaseModel):
    """
    Research Planning 层记录科研人员确认的主分析方法。

    这里不再因为当前引擎只实现了某一种算法，
    就把 Research Plan 强制限制在该方法。

    是否可自动执行，由后续 Capability Check / Registry 判断。
    """

    method: str | None = None


# ==========================================
# Open Issue
# ==========================================

class OpenIssue(BaseModel):
    issue_id: str
    field_path: str

    issue_type: str

    blocking: bool = True

    question: str


# ==========================================
# Candidate Research Spec V0.1
# ==========================================

class CandidateResearchSpecV01(BaseModel):

    schema_version: str = "0.1.0"

    source_question: str

    # Research Planning 层允许记录真实研究设计，
    # 不再把它与当前执行引擎能力绑定。
    study_design: str | None = None

    objective: str | None = None

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
