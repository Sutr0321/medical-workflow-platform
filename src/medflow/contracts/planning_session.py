from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from medflow.contracts.candidate_spec import (
    CandidateResearchSpecV01,
)


class PlanningMessageV03(BaseModel):
    role: Literal[
        "user",
        "assistant",
    ]

    content: str

    created_at: datetime


class PlanningSuggestionV03(BaseModel):
    """
    AI 可以提出候选建议，但建议本身不写入正式研究状态。
    只有用户在后续对话中明确接受后，才能转成 explicit update。
    """

    field_path: str

    value: Any

    label: str

    reason: str


class PlanningStateUpdateV03(BaseModel):
    """
    仅表示用户在当前消息中已经明确表达的结构化信息。
    """

    field_path: str

    value: Any

    evidence: str


class PlanningDecisionV03(BaseModel):
    """
    已经由用户明确表达/接受，或由系统进行不改变研究意图的确定性规范化记录。
    """

    field_path: str

    value: Any

    evidence: str

    source: Literal[
        "USER_EXPLICIT",
        "SYSTEM_NORMALIZATION",
    ] = "USER_EXPLICIT"

    decided_at: datetime


class PlanningAgentTurnV03(BaseModel):
    """
    LLM 每轮的内部结构化输出。

    assistant_message 才展示给用户；
    updates / suggestions 供后台状态机使用。
    """

    assistant_message: str

    explicit_updates: list[
        PlanningStateUpdateV03
    ] = Field(
        default_factory=list
    )

    suggestions: list[
        PlanningSuggestionV03
    ] = Field(
        default_factory=list
    )


class PlanningSessionV03(BaseModel):
    schema_version: Literal[
        "0.3.0"
    ] = "0.3.0"

    session_id: str

    status: Literal[
        "DISCUSSING",
        "READY_TO_FREEZE",
        "FROZEN",
    ] = "DISCUSSING"

    messages: list[
        PlanningMessageV03
    ] = Field(
        default_factory=list
    )

    current_candidate: CandidateResearchSpecV01

    confirmed_fields: list[str] = Field(
        default_factory=list
    )

    decisions: list[
        PlanningDecisionV03
    ] = Field(
        default_factory=list
    )

    pending_suggestions: list[
        PlanningSuggestionV03
    ] = Field(
        default_factory=list
    )

    created_at: datetime

    updated_at: datetime
