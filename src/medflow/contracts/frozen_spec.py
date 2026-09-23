from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from medflow.contracts.reviewed_spec import (
    ReviewedResearchSpecV01,
)


class FrozenResearchSpecV01(BaseModel):
    """
    已人工确认并正式冻结的 Research Spec。

    从这里开始：
    - 不允许 AI 修改
    - 不允许直接修改
    - 修改研究方案必须创建新版本
    """

    model_config = ConfigDict(
        frozen=True
    )

    spec_id: str

    spec_version: int = Field(
        ge=1
    )

    status: Literal[
        "FROZEN"
    ] = "FROZEN"

    content_hash: str

    frozen_at: datetime

    research_spec: ReviewedResearchSpecV01