from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class ResearchDatasetPlanV02(BaseModel):
    """
    研究计划中确认的数据来源名称。

    注意：
    这里不是数据文件路径，也不是数据表/变量绑定。
    """
    name: str


class ResearchPopulationPlanV02(BaseModel):
    description: str | None = None
    age_min: float
    age_max: float | None = None


class ResearchExposurePlanV02(BaseModel):
    """
    研究计划中的暴露语义。

    preferred_unit 只是研究者希望解释/报告时采用的单位，
    不代表真实数据源中的实际单位。

    真实源变量单位必须在 Data Binding 阶段验证。
    """
    name: str

    data_type: Literal[
        "continuous",
        "categorical",
        "binary",
    ]

    analysis_form: Literal[
        "continuous",
        "categorical",
    ]

    preferred_unit: str | None = None


class ResearchOutcomePlanV02(BaseModel):
    """
    研究计划中的结局语义。

    definition 是科研人员确认后的自然语言研究定义，
    不是可直接执行的变量派生表达式。

    真正的 source column / coding / derivation
    留到 Data Binding。
    """
    name: str

    data_type: Literal[
        "binary",
    ]

    definition: str


class ResearchMissingDataPlanV02(BaseModel):
    strategy: Literal[
        "complete_case_global",
    ]


class ResearchAnalysisPlanV02(BaseModel):
    method: Literal[
        "logistic_regression",
    ]


class ResearchPlanV02(BaseModel):
    """
    人工审核完成后的正式研究计划。

    它已经冻结研究意图，
    但还不是“可直接执行”的统计任务。

    后续需要经过 Data Binding，
    才能生成真正的 Executable Analysis Spec。
    """

    schema_version: Literal[
        "0.2.1"
    ] = "0.2.1"

    source_question: str

    study_design: Literal[
        "cross_sectional",
    ]

    objective: Literal[
        "association",
    ]

    dataset: ResearchDatasetPlanV02

    population: ResearchPopulationPlanV02

    exposure: ResearchExposurePlanV02

    outcome: ResearchOutcomePlanV02

    covariates: list[str] = Field(
        default_factory=list
    )

    missing_data: ResearchMissingDataPlanV02

    analysis: ResearchAnalysisPlanV02


class FrozenResearchPlanV02(BaseModel):
    """
    正式冻结后的研究计划。

    从这里开始：
    - 不允许 AI 修改
    - 不允许直接修改
    - 修改研究计划必须创建新版本

    但它仍需经过 Data Binding 才能执行。
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

    research_plan: ResearchPlanV02
