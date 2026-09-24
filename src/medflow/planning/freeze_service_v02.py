import hashlib
import json
import uuid
from datetime import datetime, timezone

from medflow.contracts.research_plan import (
    FrozenResearchPlanV03,
    ResearchPlanV03,
)
from medflow.contracts.review_log import (
    ReviewDecisionLogV02,
)


class ResearchPlanFreezeServiceV03:
    """
    V0.3 Rich Research Plan 冻结服务。
    """

    @staticmethod
    def freeze(
        *,
        research_plan: ResearchPlanV03,
        review_log: ReviewDecisionLogV02,
    ) -> FrozenResearchPlanV03:

        if (
            review_log.status
            != "COMPLETE"
        ):
            raise ValueError(
                "Review Log 尚未完成，不能冻结。"
            )

        content_hash = (
            ResearchPlanFreezeServiceV03
            ._calculate_hash(
                research_plan
            )
        )

        return FrozenResearchPlanV03(
            plan_id=(
                "RP3-"
                + uuid.uuid4().hex[
                    :12
                ].upper()
            ),
            plan_version=1,
            status="FROZEN",
            content_hash=content_hash,
            frozen_at=datetime.now(
                timezone.utc
            ),
            review_id=(
                review_log.review_id
            ),
            reviewed_by=(
                review_log.reviewed_by
            ),
            research_plan=(
                research_plan
            ),
        )

    @staticmethod
    def _calculate_hash(
        research_plan: ResearchPlanV03,
    ) -> str:

        canonical_json = json.dumps(
            research_plan.model_dump(
                mode="json"
            ),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

        return hashlib.sha256(
            canonical_json.encode(
                "utf-8"
            )
        ).hexdigest()
