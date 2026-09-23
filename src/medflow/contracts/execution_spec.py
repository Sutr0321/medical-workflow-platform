from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class ExecutionDatasetV02(BaseModel):
    name: str


class ExecutionPopulationV02(BaseModel):
    description: str | None = None

    age_min: float

    age_max: float | None = None


class ExecutionExposureV02(BaseModel):
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

    unit: str | None = None


class ExecutionOutcomeV02(BaseModel):
    name: str

    data_type: Literal[
        "binary",
    ]

    definition: str


class ExecutionMissingDataV02(BaseModel):
    strategy: Literal[
        "complete_case_global",
    ]


class ExecutionAnalysisV02(BaseModel):
    method: Literal[
        "logistic_regression",
    ]


class ExecutionResearchSpecV02(BaseModel):
    """
    真正给后续 Rule / Workflow 使用的执行版 Research Spec。

    这里不再保存：
    - AI 推荐理由
    - alternatives
    - open_issues
    - confirmation_questions
    - 数据真实列名

    真实列名属于后续 Data Binding。
    """

    schema_version: Literal[
        "0.2.0"
    ] = "0.2.0"

    source_question: str

    study_design: Literal[
        "cross_sectional",
    ]

    objective: Literal[
        "association",
    ]

    dataset: ExecutionDatasetV02

    population: ExecutionPopulationV02

    exposure: ExecutionExposureV02

    outcome: ExecutionOutcomeV02

    covariates: list[str] = Field(
        default_factory=list
    )

    missing_data: ExecutionMissingDataV02

    analysis: ExecutionAnalysisV02


class FrozenExecutionSpecV02(BaseModel):
    """
    V0.2 正式冻结后的机器执行方案。
    """

    model_config = ConfigDict(
        frozen=True
    )

    spec_id: str

    spec_version: int = Field(
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

    execution_spec: ExecutionResearchSpecV02
