import re

from medflow.contracts.candidate_spec import (
    CandidateResearchSpecV01,
)
from medflow.contracts.execution_spec import (
    ExecutionAnalysisV02,
    ExecutionDatasetV02,
    ExecutionExposureV02,
    ExecutionMissingDataV02,
    ExecutionOutcomeV02,
    ExecutionPopulationV02,
    ExecutionResearchSpecV02,
)
from medflow.contracts.review_log import (
    ReviewDecisionLogV02,
)
from medflow.spec.readiness import (
    CandidateReadiness,
    CandidateReadinessChecker,
)


class ExecutionSpecBuilderV02:
    """
    把“人机讨论/审核层”压缩成纯机器执行语义。

    重要边界：
    - 不保留推荐理由
    - 不保留备选项
    - 不保留 open issues
    - 不保留真实数据列名
    - 不保留 API / UI 状态

    真正的数据列映射属于后续 Data Binding。
    """

    FUZZY_PATTERNS = (
        r"待确认",
        r"需确认",
        r"进一步确认",
        r"取决于",
        r"视情况",
        r"若为横断面",
        r"若为队列",
        r"可选",
    )

    @staticmethod
    def build(
        *,
        reviewed_candidate: CandidateResearchSpecV01,
        review_log: ReviewDecisionLogV02,
    ) -> ExecutionResearchSpecV02:

        readiness = (
            CandidateReadinessChecker
            .check(
                reviewed_candidate
            )
        )

        if (
            readiness
            != CandidateReadiness.READY_FOR_REVIEW
        ):
            raise ValueError(
                "Research Spec 仍存在 blocking issue，"
                "不能生成 Execution Spec。"
            )

        ExecutionSpecBuilderV02._require(
            reviewed_candidate.dataset.name,
            "dataset.name",
        )

        ExecutionSpecBuilderV02._require(
            reviewed_candidate.exposure.name,
            "exposure.name",
        )

        ExecutionSpecBuilderV02._require(
            reviewed_candidate.outcome.name,
            "outcome.name",
        )

        ExecutionSpecBuilderV02._scan_fuzzy_text(
            reviewed_candidate
            .model_dump()
        )

        spec = ExecutionResearchSpecV02(
            source_question=(
                reviewed_candidate
                .source_question
            ),
            study_design=(
                reviewed_candidate
                .study_design
            ),
            objective=(
                reviewed_candidate
                .objective
            ),
            dataset=ExecutionDatasetV02(
                name=(
                    reviewed_candidate
                    .dataset
                    .name
                )
            ),
            population=(
                ExecutionPopulationV02(
                    description=(
                        reviewed_candidate
                        .population
                        .description
                    ),
                    age_min=(
                        reviewed_candidate
                        .population
                        .age_min
                    ),
                    age_max=(
                        reviewed_candidate
                        .population
                        .age_max
                    ),
                )
            ),
            exposure=ExecutionExposureV02(
                name=(
                    reviewed_candidate
                    .exposure
                    .name
                ),
                data_type=(
                    reviewed_candidate
                    .exposure
                    .data_type
                ),
                analysis_form=(
                    reviewed_candidate
                    .exposure
                    .analysis_form
                ),
                unit=(
                    reviewed_candidate
                    .exposure
                    .unit
                ),
            ),
            outcome=ExecutionOutcomeV02(
                name=(
                    reviewed_candidate
                    .outcome
                    .name
                ),
                data_type=(
                    reviewed_candidate
                    .outcome
                    .data_type
                ),
                definition=(
                    reviewed_candidate
                    .outcome
                    .definition
                ),
            ),
            covariates=[
                item.name
                for item
                in reviewed_candidate
                .covariates
            ],
            missing_data=(
                ExecutionMissingDataV02(
                    strategy=(
                        reviewed_candidate
                        .missing_data
                        .strategy
                    )
                )
            ),
            analysis=ExecutionAnalysisV02(
                method=(
                    reviewed_candidate
                    .analysis
                    .method
                )
            ),
        )

        # review_log 参数被显式要求，
        # 表示 Execution Spec 必须来自一次完整审核，
        # 而不能绕过 Review Engine 直接构造。
        if review_log.status != "COMPLETE":
            raise ValueError(
                "Review Log 未完成。"
            )

        return spec

    @staticmethod
    def _require(
        value,
        field_path: str,
    ) -> None:

        if value is None:
            raise ValueError(
                f"执行层必填字段缺失：{field_path}"
            )

        if (
            isinstance(value, str)
            and not value.strip()
        ):
            raise ValueError(
                f"执行层必填字段为空：{field_path}"
            )

    @staticmethod
    def _scan_fuzzy_text(
        value,
        path: str = "",
    ) -> None:

        if isinstance(value, dict):

            for key, sub_value in (
                value.items()
            ):

                new_path = (
                    f"{path}.{key}"
                    if path
                    else key
                )

                if (
                    new_path
                    == "open_issues"
                ):
                    continue

                ExecutionSpecBuilderV02._scan_fuzzy_text(
                    sub_value,
                    new_path,
                )

            return

        if isinstance(value, list):

            for index, sub_value in enumerate(
                value
            ):

                ExecutionSpecBuilderV02._scan_fuzzy_text(
                    sub_value,
                    f"{path}[{index}]",
                )

            return

        if not isinstance(
            value,
            str,
        ):
            return

        for pattern in (
            ExecutionSpecBuilderV02
            .FUZZY_PATTERNS
        ):

            if re.search(
                pattern,
                value,
            ):
                raise ValueError(
                    f"字段 {path} 仍包含模糊表述："
                    f"{value}"
                )
