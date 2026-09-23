from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    Field,
)

from medflow.contracts.algorithm_io import (
    AlgorithmEstimateV01,
)


class ResultRecordV01(BaseModel):
    """
    Result Registry V0.1
    单次算法运行结果的标准保存格式。

    注意：
    当前只是 Result Schema，
    还没有开始实现 Result Registry。
    """

    schema_version: Literal[
        "0.1.0"
    ] = "0.1.0"

    # ======================================
    # Result 身份
    # ======================================

    result_id: str

    # ======================================
    # 来源 Research Spec
    # ======================================

    spec_id: str

    spec_version: int = Field(
        ge=1
    )

    # ======================================
    # Algorithm
    # ======================================

    algorithm_name: str

    algorithm_version: str

    # ======================================
    # Execution Status
    # ======================================

    status: Literal[
        "SUCCESS",
        "FAILED",
    ]

    # ======================================
    # Sample Size
    # ======================================

    n_used: int = Field(
        ge=0
    )

    # ======================================
    # Statistical Results
    # ======================================

    estimates: list[
        AlgorithmEstimateV01
    ] = Field(
        default_factory=list
    )

    # ======================================
    # Timestamp
    # ======================================

    created_at: datetime