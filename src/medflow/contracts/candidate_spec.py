from typing import Any

from pydantic import BaseModel, Field


# ==========================================
# Dataset
# ==========================================

class CandidateDataset(BaseModel):
    name: str | None = None

    # 研究者明确指定的调查周期 / 数据版本。
    # 对 NHANES 可保存类似：
    # "2013-2014, 2015-2016, 2017-2018"
    version: str | None = None

    # 真实本地路径仍属于 Data Binding。
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

    data_type: str | None = None

    # 当前阶段只是计划报告单位，
    # 真实源单位必须在 Data Binding 阶段核对。
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

    data_type: str | None = None

    coding: CandidateBinaryCoding | None = Field(
        default_factory=CandidateBinaryCoding
    )

    # 主结局定义。
    definition: str | None = None

    # 与主结局定义分离保存的替代定义 / 敏感性分析定义。
    # 例如：
    # ["140/90 mmHg 标准"]
    sensitivity_definitions: list[str] = Field(
        default_factory=list
    )


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
    Research Planning 层的缺失值计划。

    strategy 保留一个简洁的人类可读总策略，
    其余字段把“固定策略”和“数据依赖条件策略”拆开，
    避免把整段科研规则都塞进一个字符串。
    """

    strategy: str | None = None

    # fixed / data_dependent
    mode: str | None = None

    # 决策前需要评估什么。
    assessment: list[str] = Field(
        default_factory=list
    )

    # 条件式决策规则。
    decision_rule: str | None = None

    # 敏感性分析原则。
    sensitivity_plan: str | None = None


# ==========================================
# Analysis
# ==========================================

class CandidateAnalysis(BaseModel):
    """
    Research Planning 层的分析计划。

    method 仍保留用于兼容现有执行能力检查，
    但不再让 method 一个字符串承担整份统计方案。
    """

    # 主模型 / 主分析方法。
    method: str | None = None

    # 主要效应量，例如 OR / PR / beta。
    effect_measure: str | None = None

    # 例如 0.95。
    ci_level: float | None = None

    # 是否明确要求复杂抽样 / survey design。
    survey_design_required: bool | None = None

    # 次要分析，例如 RCS。
    secondary_analyses: list[str] = Field(
        default_factory=list
    )

    # 敏感性分析，例如 robust Poisson PR。
    sensitivity_analyses: list[str] = Field(
        default_factory=list
    )


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

    schema_version: str = "0.1.1"

    source_question: str

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
