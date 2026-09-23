import hashlib
import json
import uuid
from datetime import datetime, timezone

from medflow.contracts.execution_spec import (
    ExecutionResearchSpecV02,
    FrozenExecutionSpecV02,
)
from medflow.contracts.review_log import (
    ReviewDecisionLogV02,
)


class ExecutionSpecFreezeServiceV02:
    """
    V0.2 Execution Spec 冻结服务。

    从这里开始，后续 Rule / YAML / Workflow
    只读取 frozen.execution_spec。
    """

    @staticmethod
    def freeze(
        *,
        execution_spec: ExecutionResearchSpecV02,
        review_log: ReviewDecisionLogV02,
    ) -> FrozenExecutionSpecV02:

        if (
            review_log.status
            != "COMPLETE"
        ):
            raise ValueError(
                "Review Log 尚未完成，不能冻结。"
            )

        content_hash = (
            ExecutionSpecFreezeServiceV02
            ._calculate_hash(
                execution_spec
            )
        )

        return FrozenExecutionSpecV02(
            spec_id=(
                "RS2-"
                + uuid.uuid4().hex[
                    :12
                ].upper()
            ),
            spec_version=1,
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
            execution_spec=(
                execution_spec
            ),
        )

    @staticmethod
    def _calculate_hash(
        execution_spec: ExecutionResearchSpecV02,
    ) -> str:

        canonical_json = json.dumps(
            execution_spec.model_dump(
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
