import json
from pathlib import Path

from medflow.contracts.planning_session import (
    PlanningSessionV03,
)
from medflow.contracts.research_plan import (
    FrozenResearchPlanV03,
)
from medflow.contracts.review_log import (
    ReviewDecisionLogV02,
)


class ConversationPlanningStoreV03:
    """
    保存对话规划的完整审计产物。

    会话与正式 Research Plan 分开保存。
    """

    def __init__(
        self,
        root_dir: str | Path,
    ):
        self.root_dir = Path(
            root_dir
        )

    def save_final_bundle(
        self,
        *,
        session: PlanningSessionV03,
        review_log: ReviewDecisionLogV02,
        frozen_plan: FrozenResearchPlanV03,
    ) -> Path:

        output_dir = (
            self.root_dir
            / frozen_plan.plan_id
            / (
                f"v{frozen_plan.plan_version}"
            )
        )

        if output_dir.exists():
            raise FileExistsError(
                "Conversational planning bundle "
                f"已存在，禁止覆盖：{output_dir}"
            )

        output_dir.mkdir(
            parents=True,
            exist_ok=False,
        )

        (
            output_dir
            / "planning_session.json"
        ).write_text(
            session.model_dump_json(
                indent=2
            ),
            encoding="utf-8",
        )

        (
            output_dir
            / "review_log.json"
        ).write_text(
            review_log.model_dump_json(
                indent=2
            ),
            encoding="utf-8",
        )

        (
            output_dir
            / "research_plan.json"
        ).write_text(
            frozen_plan.model_dump_json(
                indent=2
            ),
            encoding="utf-8",
        )

        transcript = [
            {
                "role": item.role,
                "content": item.content,
                "created_at": (
                    item.created_at.isoformat()
                ),
            }
            for item in session.messages
        ]

        (
            output_dir
            / "transcript.json"
        ).write_text(
            json.dumps(
                transcript,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        return output_dir
