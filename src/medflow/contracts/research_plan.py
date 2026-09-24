from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class ResearchDatasetPlanV03(BaseModel):
    """
    正式 Research Plan 中的数据来源语义。

    version 保存研究者已经明确指定的调查周期/数据版本。
    真实文件路径与真实变量绑定仍属于 Data Binding。
    """

    name: str

    version: str | None = None


class ResearchPopulationPlanV03(BaseModel):
    description: str | None = None
    age_min: float
    age_max: float | None = None


class ResearchExposurePlanV03(BaseModel):
    name: str
    data_type: str
    analysis_form: str

    # 计划报告单位，不代表真实源单位。
    preferred_unit: str | None = None


class ResearchOutcomePlanV03(BaseModel):
    """
    definition 保存主定义；
    sensitivity_definitions 保存替代阈值/敏感性分析定义。
    """

    name: str
    data_type: str
    definition: str

    sensitivity_definitions: list[str] = Field(
        default_factory=list
    )


class ResearchMissingDataPlanV03(BaseModel):
    """
    缺失值计划支持固定策略和数据依赖策略。
    """

    strategy: str

    mode: str | None = None

    assessment: list[str] = Field(
        default_factory=list
    )

    decision_rule: str | None = None

    sensitivity_plan: str | None = None


class ResearchAnalysisPlanV03(BaseModel):
    """
    主模型与补充/敏感性分析分离保存。
    """

    primary_model: str

    effect_measure: str | None = None

    ci_level: float | None = None

    survey_design_required: bool | None = None

    secondary_analyses: list[str] = Field(
        default_factory=list
    )

    sensitivity_analyses: list[str] = Field(
        default_factory=list
    )


class ResearchPlanV03(BaseModel):
    """
    V0.3 Rich Research Plan。

    冻结研究意图，不冻结真实数据列名、编码、权重变量、
    PSU/strata 变量或可执行派生表达式。
    """

    schema_version: Literal[
        "0.3.0"
    ] = "0.3.0"

    source_question: str

    study_design: str

    objective: str

    dataset: ResearchDatasetPlanV03

    population: ResearchPopulationPlanV03

    exposure: ResearchExposurePlanV03

    outcome: ResearchOutcomePlanV03

    covariates: list[str] = Field(
        default_factory=list
    )

    missing_data: ResearchMissingDataPlanV03

    analysis: ResearchAnalysisPlanV03


class FrozenResearchPlanV03(BaseModel):
    """
    正式冻结后的 Rich Research Plan。
    """

    model_config = ConfigDict(
        frozen=True
    )

    plan_id: str

    plan_version: int = Field(
        default=1,
        ge=1,
    )

    status: Literal[
        "FROZEN"
    ] = "FROZEN"

    content_hash: str

    frozen_at: datetime

    review_id: str

    reviewed_by: str

    research_plan: ResearchPlanV03
