import re

from medflow.contracts.candidate_spec import (
    CandidateResearchSpecV01,
)
from medflow.contracts.research_plan import (
    ResearchAnalysisPlanV03,
    ResearchDatasetPlanV03,
    ResearchExposurePlanV03,
    ResearchMissingDataPlanV03,
    ResearchOutcomePlanV03,
    ResearchPlanV03,
    ResearchPopulationPlanV03,
)
from medflow.contracts.review_log import (
    ReviewDecisionLogV02,
)
from medflow.spec.readiness import (
    CandidateReadiness,
    CandidateReadinessChecker,
)


class ResearchPlanBuilderV03:
    """
    把审核后的 Candidate Research Spec
    压缩成正式 Rich Research Plan V0.3。

    这里冻结研究意图，不冻结真实源变量绑定。
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
    ) -> ResearchPlanV03:

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

        required = {
            "study_design": reviewed_candidate.study_design,
            "objective": reviewed_candidate.objective,
            "dataset.name": reviewed_candidate.dataset.name,
            "population.age_min": reviewed_candidate.population.age_min,
            "exposure.name": reviewed_candidate.exposure.name,
            "exposure.data_type": reviewed_candidate.exposure.data_type,
            "exposure.analysis_form": reviewed_candidate.exposure.analysis_form,
            "outcome.name": reviewed_candidate.outcome.name,
            "outcome.data_type": reviewed_candidate.outcome.data_type,
            "outcome.definition": reviewed_candidate.outcome.definition,
            "missing_data.strategy": reviewed_candidate.missing_data.strategy,
            "analysis.method": reviewed_candidate.analysis.method,
        }

        for field_path, value in required.items():
            ResearchPlanBuilderV03._require(
                value,
                field_path,
            )

        plan = ResearchPlanV03(
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
            dataset=ResearchDatasetPlanV03(
                name=(
                    reviewed_candidate
                    .dataset
                    .name
                ),
                version=(
                    reviewed_candidate
                    .dataset
                    .version
                ),
            ),
            population=ResearchPopulationPlanV03(
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
            exposure=ResearchExposurePlanV03(
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
            outcome=ResearchOutcomePlanV03(
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
                sensitivity_definitions=(
                    reviewed_candidate
                    .outcome
                    .sensitivity_definitions
                ),
            ),
            covariates=[
                item.name
                for item in reviewed_candidate
                .covariates
            ],
            missing_data=ResearchMissingDataPlanV03(
                strategy=(
                    reviewed_candidate
                    .missing_data
                    .strategy
                ),
                mode=(
                    reviewed_candidate
                    .missing_data
                    .mode
                ),
                assessment=(
                    reviewed_candidate
                    .missing_data
                    .assessment
                ),
                decision_rule=(
                    reviewed_candidate
                    .missing_data
                    .decision_rule
                ),
                sensitivity_plan=(
                    reviewed_candidate
                    .missing_data
                    .sensitivity_plan
                ),
            ),
            analysis=ResearchAnalysisPlanV03(
                primary_model=(
                    reviewed_candidate
                    .analysis
                    .method
                ),
                effect_measure=(
                    reviewed_candidate
                    .analysis
                    .effect_measure
                ),
                ci_level=(
                    reviewed_candidate
                    .analysis
                    .ci_level
                ),
                survey_design_required=(
                    reviewed_candidate
                    .analysis
                    .survey_design_required
                ),
                secondary_analyses=(
                    reviewed_candidate
                    .analysis
                    .secondary_analyses
                ),
                sensitivity_analyses=(
                    reviewed_candidate
                    .analysis
                    .sensitivity_analyses
                ),
            ),
        )

        semantic_data = (
            plan.model_dump(
                exclude={
                    "source_question"
                }
            )
        )

        ResearchPlanBuilderV03._scan_fuzzy_text(
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
            for key, sub_value in value.items():
                new_path = (
                    f"{path}.{key}"
                    if path
                    else key
                )
                ResearchPlanBuilderV03._scan_fuzzy_text(
                    sub_value,
                    new_path,
                )
            return

        if isinstance(value, list):
            for index, sub_value in enumerate(value):
                ResearchPlanBuilderV03._scan_fuzzy_text(
                    sub_value,
                    f"{path}[{index}]",
                )
            return

        if not isinstance(value, str):
            return

        for pattern in (
            ResearchPlanBuilderV03
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
