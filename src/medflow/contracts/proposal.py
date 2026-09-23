from typing import Any, Literal

from pydantic import BaseModel, Field

from medflow.contracts.candidate_spec import (
    CandidateResearchSpecV01,
)


class ProposalOptionV02(BaseModel):
    """
    面向科研人员展示的候选选项。

    value 是真正写入 Research Spec 的机器值；
    label 是给人看的中文说明。
    """

    value: Any
    label: str
    description: str | None = None


class ProposalItemV02(BaseModel):
    """
    单个待审核字段的 Proposal。

    Proposal 只负责“给人看、给人选”，
    不是正式执行输入。
    """

    field_path: str
    title: str

    current_value: Any | None = None

    reason: str

    options: list[ProposalOptionV02] = Field(
        default_factory=list
    )

    allow_custom: bool = False

    blocking: bool = True

    provenance: Literal[
        "USER_EXPLICIT",
        "SYSTEM_REQUIRED",
    ]


class CandidateProposalV02(BaseModel):
    """
    Research Planning / Review Layer V0.2。

    这是候选讨论层，不允许直接作为 Workflow 输入。
    """

    schema_version: Literal[
        "0.2.0"
    ] = "0.2.0"

    proposal_id: str

    source_question: str

    candidate_spec: CandidateResearchSpecV01

    items: list[ProposalItemV02] = Field(
        default_factory=list
    )
