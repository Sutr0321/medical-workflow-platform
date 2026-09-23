import re

from medflow.contracts.candidate_spec import (
    CandidateResearchSpecV01,
)
from medflow.contracts.research_plan import (
    ResearchAnalysisPlanV02,
    ResearchDatasetPlanV02,
    ResearchExposurePlanV02,
    ResearchMissingDataPlanV02,
    ResearchOutcomePlanV02,
    ResearchPlanV02,
    ResearchPopulationPlanV02,
)
from medflow.contracts.review_log import (
    ReviewDecisionLogV02,
)
from medflow.spec.readiness import (
    CandidateReadiness,
    CandidateReadinessChecker,
)


class ResearchPlanBuilderV02:
    """
    把审核后的 Candidate Research Spec
    压缩成正式 Research Plan。

    重要边界：

    Research Plan 负责冻结“研究意图”，
    但它还不能直接执行。

    它不包含：
    - 推荐理由
    - alternatives
    - open issues
    - UI 状态
    - 真实数据列名
    - 真实编码
    - 可执行派生表达式

    后三类信息属于后续 Data Binding。
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
    ) -> ResearchPlanV02:

        if review_log.status != "COMPLETE":
            raise ValueError(
                "Review Log 未完成。"
            )

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
                "不能生成正式 Research Plan。"
            )

        ResearchPlanBuilderV02._require(
            reviewed_candidate.study_design,
            "study_design",
        )

        ResearchPlanBuilderV02._require(
            reviewed_candidate.objective,
            "objective",
        )

        ResearchPlanBuilderV02._require(
            reviewed_candidate.dataset.name,
            "dataset.name",
        )

        ResearchPlanBuilderV02._require(
            reviewed_candidate.population.age_min,
            "population.age_min",
        )

        ResearchPlanBuilderV02._require(
            reviewed_candidate.exposure.name,
            "exposure.name",
        )

        ResearchPlanBuilderV02._require(
            reviewed_candidate.exposure.data_type,
            "exposure.data_type",
        )

        ResearchPlanBuilderV02._require(
            reviewed_candidate.exposure.analysis_form,
            "exposure.analysis_form",
        )

        ResearchPlanBuilderV02._require(
            reviewed_candidate.outcome.name,
            "outcome.name",
        )

        ResearchPlanBuilderV02._require(
            reviewed_candidate.outcome.data_type,
            "outcome.data_type",
        )

        ResearchPlanBuilderV02._require(
            reviewed_candidate.outcome.definition,
            "outcome.definition",
        )

        ResearchPlanBuilderV02._require(
            reviewed_candidate.missing_data.strategy,
            "missing_data.strategy",
        )

        ResearchPlanBuilderV02._require(
            reviewed_candidate.analysis.method,
            "analysis.method",
        )

        plan = ResearchPlanV02(
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
            dataset=ResearchDatasetPlanV02(
                name=(
                    reviewed_candidate
                    .dataset
                    .name
                )
            ),
            population=ResearchPopulationPlanV02(
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
            ),
            exposure=ResearchExposurePlanV02(
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
                preferred_unit=(
                    reviewed_candidate
                    .exposure
                    .unit
                ),
            ),
            outcome=ResearchOutcomePlanV02(
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
            missing_data=ResearchMissingDataPlanV02(
                strategy=(
                    reviewed_candidate
                    .missing_data
                    .strategy
                )
            ),
            analysis=ResearchAnalysisPlanV02(
                method=(
                    reviewed_candidate
                    .analysis
                    .method
                )
            ),
        )

        # 只检查正式研究语义。
        # source_question 是原始输入，不作为执行语义，
        # 因此不参与模糊词拦截。
        semantic_data = (
            plan.model_dump(
                exclude={
                    "source_question"
                }
            )
        )

        ResearchPlanBuilderV02._scan_fuzzy_text(
            semantic_data
        )

        return plan

    @staticmethod
    def _require(
        value,
        field_path: str,
    ) -> None:

        if value is None:
            raise ValueError(
                f"正式研究计划必填字段缺失：{field_path}"
            )

        if (
            isinstance(value, str)
            and not value.strip()
        ):
            raise ValueError(
                f"正式研究计划必填字段为空：{field_path}"
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

                ResearchPlanBuilderV02._scan_fuzzy_text(
                    sub_value,
                    new_path,
                )

            return

        if isinstance(value, list):

            for index, sub_value in enumerate(
                value
            ):

                ResearchPlanBuilderV02._scan_fuzzy_text(
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
            ResearchPlanBuilderV02
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
