import uuid
from datetime import datetime, timezone
from typing import Any

from medflow.contracts.candidate_spec import (
    CandidateResearchSpecV01,
)
from medflow.contracts.proposal import (
    CandidateProposalV02,
)
from medflow.contracts.review_log import (
    ReviewDecisionLogV02,
    ReviewDecisionV02,
)
from medflow.spec.candidate_updater import (
    CandidateSpecUpdater,
)
from medflow.spec.readiness import (
    CandidateReadiness,
    CandidateReadinessChecker,
)


class ReviewEngineV02:
    """
    Generic Review Engine。

    不再为“研究设计、暴露、结局、分析方法”
    分别手写确认函数。

    输入：
    - Proposal
    - field_path -> selected_value

    输出：
    - 更新后的 Candidate Research Spec
    - 独立 Review Decision Log

    所有人工决策都有审计记录。
    """

    @staticmethod
    def apply(
        *,
        proposal: CandidateProposalV02,
        selections: dict[str, Any],
        reviewed_by: str,
    ) -> tuple[
        CandidateResearchSpecV01,
        ReviewDecisionLogV02,
    ]:

        current = proposal.candidate_spec

        item_map = {
            item.field_path: item
            for item in proposal.items
        }

        unknown = (
            set(selections)
            - set(item_map)
        )

        if unknown:
            raise ValueError(
                "存在 Proposal 中未定义的字段："
                + ", ".join(
                    sorted(unknown)
                )
            )

        answers: dict[str, Any] = {}
        decisions: list[
            ReviewDecisionV02
        ] = []

        now = datetime.now(
            timezone.utc
        )

        for field_path, item in item_map.items():

            original_value = (
                ReviewEngineV02
                ._get_value(
                    current.model_dump(),
                    field_path,
                )
            )

            if field_path not in selections:

                if (
                    original_value is None
                    and item.blocking
                ):
                    raise ValueError(
                        f"必填审核项尚未决定：{field_path}"
                    )

                decisions.append(
                    ReviewDecisionV02(
                        decision_id=(
                            "RD-"
                            + uuid.uuid4().hex[
                                :12
                            ].upper()
                        ),
                        field_path=field_path,
                        action="keep_current",
                        original_value=original_value,
                        selected_value=original_value,
                        decided_at=now,
                    )
                )

                continue

            selected_value = selections[
                field_path
            ]

            if (
                selected_value is None
                and item.blocking
            ):
                raise ValueError(
                    f"必填审核项不能清空：{field_path}"
                )

            if (
                item.options
                and selected_value is not None
            ):

                allowed_values = [
                    option.value
                    for option in item.options
                ]

                if (
                    selected_value
                    not in allowed_values
                    and not item.allow_custom
                ):
                    raise ValueError(
                        f"字段 {field_path} "
                        "选择了未注册的值："
                        f"{selected_value}"
                    )

            action = (
                "clear_optional"
                if selected_value is None
                else (
                    "keep_current"
                    if selected_value
                    == original_value
                    else (
                        "choose_option"
                        if any(
                            option.value
                            == selected_value
                            for option
                            in item.options
                        )
                        else "custom_input"
                    )
                )
            )

            answers[
                field_path
            ] = selected_value

            decisions.append(
                ReviewDecisionV02(
                    decision_id=(
                        "RD-"
                        + uuid.uuid4().hex[
                            :12
                        ].upper()
                    ),
                    field_path=field_path,
                    action=action,
                    original_value=original_value,
                    selected_value=selected_value,
                    decided_at=now,
                )
            )

        updated = (
            CandidateSpecUpdater
            .apply_answers(
                spec=current,
                answers=answers,
            )
        )

        readiness = (
            CandidateReadinessChecker
            .check(
                updated
            )
        )

        if (
            readiness
            != CandidateReadiness.READY_FOR_REVIEW
        ):
            blocking = [
                issue.field_path
                for issue
                in updated.open_issues
                if issue.blocking
            ]

            raise ValueError(
                "人工审核后仍存在 blocking issues："
                + ", ".join(blocking)
            )

        log = ReviewDecisionLogV02(
            review_id=(
                "RV-"
                + uuid.uuid4().hex[
                    :12
                ].upper()
            ),
            proposal_id=proposal.proposal_id,
            reviewed_by=reviewed_by,
            reviewed_at=now,
            decisions=decisions,
        )

        return updated, log

    @staticmethod
    def _get_value(
        data,
        field_path: str,
    ):

        if field_path == "covariates":
            return [
                item["name"]
                for item in data[
                    "covariates"
                ]
            ]

        current = data

        for token in (
            field_path.split(".")
        ):

            if not isinstance(
                current,
                dict,
            ):
                return None

            current = current.get(
                token
            )

        return current
