from datetime import datetime, timezone

from medflow.contracts.candidate_spec import (
    CandidateResearchSpecV01,
)

from medflow.contracts.reviewed_spec import (
    ReviewedResearchSpecV01,
    SemanticConfirmation,
)

from medflow.spec.readiness import (
    CandidateReadiness,
    CandidateReadinessChecker,
)


class SpecReviewService:
    """
    Research Spec 人工确认服务。

    不调用 AI。

    只有 READY_FOR_REVIEW 的 Candidate
    才允许进行人工确认。
    """

    @staticmethod
    def confirm(
        spec: CandidateResearchSpecV01,
        confirmed_by: str,
    ) -> ReviewedResearchSpecV01:

        readiness = CandidateReadinessChecker.check(
            spec
        )

        if (
            readiness
            != CandidateReadiness.READY_FOR_REVIEW
        ):
            raise ValueError(
                "Research Spec 尚未达到 "
                "READY_FOR_REVIEW 状态，"
                "不能进行人工确认。"
            )

        confirmation = SemanticConfirmation(
            confirmed=True,
            confirmed_by=confirmed_by,
            confirmed_at=datetime.now(
                timezone.utc
            ),
        )

        return ReviewedResearchSpecV01(
            **spec.model_dump(),
            confirmation=confirmation,
        )