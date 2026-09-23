from pathlib import Path

from medflow.contracts.execution_spec import (
    FrozenExecutionSpecV02,
)
from medflow.contracts.proposal import (
    CandidateProposalV02,
)
from medflow.contracts.review_log import (
    ReviewDecisionLogV02,
)


class ResearchPlanningStoreV02:
    """
    V0.2 Research Planning Artifact Store。

    每次正式冻结保存三份彼此分离的产物：

    proposal.json
        人机讨论/候选层

    review_log.json
        人工审核审计记录

    execution_spec.json
        后续 Rule / Workflow 唯一读取的执行语义
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
        frozen_spec: FrozenExecutionSpecV02,
    ) -> Path:

        version_dir = (
            self.root_dir
            / frozen_spec.spec_id
            / (
                f"v{frozen_spec.spec_version}"
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
            / "execution_spec.json"
        ).write_text(
            frozen_spec.model_dump_json(
                indent=2
            ),
            encoding="utf-8",
        )

        return version_dir
