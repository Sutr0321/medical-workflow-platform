from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ReviewDecisionV02(BaseModel):
    """
    一个字段的一次人工决策记录。
    """

    decision_id: str

    field_path: str

    action: Literal[
        "keep_current",
        "choose_option",
        "custom_input",
        "clear_optional",
    ]

    original_value: Any | None = None
    selected_value: Any | None = None

    note: str | None = None

    decided_at: datetime


class ReviewDecisionLogV02(BaseModel):
    """
    完整人工审核日志。

    它和 Frozen Execution Spec 分开保存，
    用于回答“谁改了什么、最终为什么是这个值”。
    """

    schema_version: Literal[
        "0.2.0"
    ] = "0.2.0"

    review_id: str

    proposal_id: str

    reviewed_by: str

    reviewed_at: datetime

    status: Literal[
        "COMPLETE"
    ] = "COMPLETE"

    decisions: list[
        ReviewDecisionV02
    ] = Field(
        default_factory=list
    )
