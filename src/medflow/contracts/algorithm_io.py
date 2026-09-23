from typing import Literal

from pydantic import (
    BaseModel,
    Field,
)


# ==========================================
# Algorithm Input
# ==========================================

class AlgorithmInputV01(BaseModel):
    """
    Algorithm Block V0.1 统一输入格式。

    当前版本只支持 Logistic Regression。
    """

    schema_version: Literal[
        "0.1.0"
    ] = "0.1.0"

    algorithm_name: Literal[
        "logistic_regression"
    ] = "logistic_regression"

    algorithm_version: str

    # --------------------------------------
    # 数据来源
    # --------------------------------------

    dataset_ref: str

    # --------------------------------------
    # Data Binding 之后得到的真实列名
    # --------------------------------------

    outcome_column: str

    exposure_column: str

    covariate_columns: list[str] = Field(
        default_factory=list
    )


# ==========================================
# 单个统计估计结果
# ==========================================

class AlgorithmEstimateV01(BaseModel):
    """
    单个 term 的统计结果。
    """

    term: str

    measure: Literal[
        "odds_ratio"
    ] = "odds_ratio"

    estimate: float

    ci_level: float = Field(
        default=0.95,
        gt=0,
        lt=1,
    )

    ci_lower: float

    ci_upper: float

    p_value: float = Field(
        ge=0,
        le=1,
    )


# ==========================================
# Algorithm Output
# ==========================================

class AlgorithmOutputV01(BaseModel):
    """
    Algorithm Block V0.1 统一输出格式。
    """

    schema_version: Literal[
        "0.1.0"
    ] = "0.1.0"

    algorithm_name: Literal[
        "logistic_regression"
    ] = "logistic_regression"

    algorithm_version: str

    status: Literal[
        "SUCCESS",
        "FAILED",
    ]

    n_used: int = Field(
        ge=0
    )

    estimates: list[
        AlgorithmEstimateV01
    ] = Field(
        default_factory=list
    )

    warnings: list[str] = Field(
        default_factory=list
    )

    error_message: str | None = None