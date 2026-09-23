from pathlib import Path

from medflow.contracts.proposal import (
    CandidateProposalV02,
)
from medflow.contracts.research_plan import (
    FrozenResearchPlanV02,
)
from medflow.contracts.review_log import (
    ReviewDecisionLogV02,
)


class ResearchPlanningStoreV02:
    """
    V0.2 Research Planning Artifact Store。

    每次正式冻结保存三份彼此分离的产物：

    proposal.json
        候选讨论层

    review_log.json
        人工审核审计记录

    research_plan.json
        已冻结的正式研究计划

    注意：
    research_plan.json 仍不能直接执行。
    后续还需要 Data Binding。
    """

    def __init__(
        self,
        root_dir: str | Path,
    ):
        self.root_dir = Path(
            root_dir
        )

    def save_bundle(
        self,
        *,
        proposal: CandidateProposalV02,
        review_log: ReviewDecisionLogV02,
        frozen_plan: FrozenResearchPlanV02,
    ) -> Path:

        version_dir = (
            self.root_dir
            / frozen_plan.plan_id
            / (
                f"v{frozen_plan.plan_version}"
            )
        )

        if version_dir.exists():
            raise FileExistsError(
                "Research Planning V0.2 bundle "
                f"已存在，禁止覆盖：{version_dir}"
            )

        version_dir.mkdir(
            parents=True,
            exist_ok=False,
        )

        (
            version_dir
            / "proposal.json"
        ).write_text(
            proposal.model_dump_json(
                indent=2
            ),
            encoding="utf-8",
        )

        (
            version_dir
            / "review_log.json"
        ).write_text(
            review_log.model_dump_json(
                indent=2
            ),
            encoding="utf-8",
        )

        (
            version_dir
            / "research_plan.json"
        ).write_text(
            frozen_plan.model_dump_json(
                indent=2
            ),
            encoding="utf-8",
        )

        return version_dir
