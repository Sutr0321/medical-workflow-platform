from enum import Enum

from medflow.contracts.candidate_spec import (
    CandidateResearchSpecV01,
)


class CandidateReadiness(str, Enum):
    NEEDS_INPUT = "NEEDS_INPUT"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"


class CandidateReadinessChecker:
    """
    Candidate Research Spec 语义层状态判断。

    不使用 AI。
    完全依据固定规则判断。
    """

    @staticmethod
    def check(
        spec: CandidateResearchSpecV01,
    ) -> CandidateReadiness:

        # 只要还存在 blocking issue，
        # 就不能进入人工最终确认。
        has_blocking_issue = any(
            issue.blocking
            for issue in spec.open_issues
        )

        if has_blocking_issue:
            return CandidateReadiness.NEEDS_INPUT

        return CandidateReadiness.READY_FOR_REVIEW