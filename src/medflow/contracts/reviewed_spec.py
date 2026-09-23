from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from medflow.contracts.candidate_spec import (
    CandidateResearchSpecV01,
)


class SemanticConfirmation(BaseModel):
    """
    科研人员对研究方案语义内容的人工确认记录。
    """

    confirmed: Literal[True] = True

    confirmed_by: str

    confirmed_at: datetime


class ReviewedResearchSpecV01(
    CandidateResearchSpecV01
):
    """
    已完成人工语义确认的 Research Spec。

    注意：
    此时还没有完成数据绑定，
    所以还不是最终 Frozen / Executable Spec。
    """

    review_status: Literal[
        "READY_FOR_DATA_BINDING"
    ] = "READY_FOR_DATA_BINDING"

    confirmation: SemanticConfirmation