import uuid
from datetime import datetime, timezone

from medflow.contracts.planning_session import (
    PlanningSessionV03,
)
from medflow.contracts.review_log import (
    ReviewDecisionLogV02,
    ReviewDecisionV02,
)
from medflow.conversation.readiness_v03 import (
    ConversationalReadinessV03,
)
from medflow.planning.freeze_service_v02 import (
    ResearchPlanFreezeServiceV03,
)
from medflow.planning.research_plan_builder import (
    ResearchPlanBuilderV03,
)


class ConversationalPlanningFinalizerV03:
    """
    把已讨论完整的 Planning Session 冻结为 Research Plan。

    冻结完全由确定性代码执行。
    """

    @staticmethod
    def finalize(
        *,
        session: PlanningSessionV03,
        reviewed_by: str,
    ):

        blockers = (
            ConversationalReadinessV03
            .blocking_reasons(
                session.current_candidate
            )
        )

        if blockers:
            raise ValueError(
                "当前研究方案尚不能冻结：\n- "
                + "\n- ".join(blockers)
            )

        if (
            session.status
            != "READY_TO_FREEZE"
        ):
            raise ValueError(
                "当前 Planning Session 状态不是 READY_TO_FREEZE。"
            )

        now = datetime.now(
            timezone.utc
        )

        review_decisions = []

        previous_values = {}

        for item in session.decisions:

            original_value = (
                previous_values.get(
                    item.field_path
                )
            )

            review_decisions.append(
                ReviewDecisionV02(
                    decision_id=(
                        "RD-"
                        + uuid.uuid4().hex[
                            :12
                        ].upper()
                    ),
                    field_path=(
                        item.field_path
                    ),
                    action="custom_input",
                    original_value=(
                        original_value
                    ),
                    selected_value=(
                        item.value
                    ),
                    note=(
                        (
                            "对话式规划中由用户明确表达。"
                            if item.source
                            == "USER_EXPLICIT"
                            else (
                                "系统进行了不改变研究意图的"
                                "确定性规范化。"
                            )
                        )
                        + f" 证据：{item.evidence}"
                    ),
                    decided_at=(
                        item.decided_at
                    ),
                )
            )

            previous_values[
                item.field_path
            ] = item.value

        review_log = ReviewDecisionLogV02(
            review_id=(
                "RV-"
                + uuid.uuid4().hex[
                    :12
                ].upper()
            ),
            proposal_id=(
                "CONVERSATION:"
                + session.session_id
            ),
            reviewed_by=reviewed_by,
            reviewed_at=now,
            status="COMPLETE",
            decisions=review_decisions,
        )

        research_plan = (
            ResearchPlanBuilderV03
            .build(
                reviewed_candidate=(
                    session.current_candidate
                ),
                review_log=review_log,
            )
        )

        frozen_plan = (
            ResearchPlanFreezeServiceV03
            .freeze(
                research_plan=(
                    research_plan
                ),
                review_log=review_log,
            )
        )

        frozen_session = (
            session.model_copy(
                update={
                    "status": "FROZEN",
                    "updated_at": now,
                }
            )
        )

        return (
            frozen_session,
            review_log,
            frozen_plan,
        )
