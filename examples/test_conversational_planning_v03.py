import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


project_root = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

src_path = (
    project_root
    / "src"
)

sys.path.insert(
    0,
    str(src_path),
)


from medflow.contracts.candidate_spec import (
    CandidateAnalysis,
    CandidateCovariate,
    CandidateDataset,
    CandidateExposure,
    CandidateMissingData,
    CandidateOutcome,
    CandidatePopulation,
    CandidateResearchSpecV01,
)
from medflow.contracts.planning_session import (
    PlanningDecisionV03,
    PlanningMessageV03,
    PlanningSessionV03,
)
from medflow.conversation.commands import (
    PlanningCommandRouterV03,
)
from medflow.conversation.finalizer import (
    ConversationalPlanningFinalizerV03,
)
from medflow.conversation.preview import (
    ResearchPlanPreviewV03,
)
from medflow.conversation.readiness_v03 import (
    ConversationalReadinessV03,
)
from medflow.conversation.store_v03 import (
    ConversationPlanningStoreV03,
)
from medflow.execution.capability import (
    ExecutionCapabilityCheckerV03,
)
from medflow.spec.candidate_validator import (
    CandidateSpecValidator,
)


def build_complete_candidate(
    *,
    missing_strategy: str = "complete_case_global",
    analysis_method: str = "logistic_regression",
):

    candidate = CandidateResearchSpecV01(
        source_question=(
            "研究 NHANES 2017-2018 中"
            "20岁及以上成年人维生素D与高血压的关联。"
        ),
        study_design="cross_sectional",
        objective="association",
        dataset=CandidateDataset(
            name="NHANES",
            version="2017-2018",
        ),
        population=CandidatePopulation(
            age_min=20,
        ),
        exposure=CandidateExposure(
            name="25-羟基维生素D",
            data_type="continuous",
            unit="ng/mL",
            analysis_form="continuous",
        ),
        outcome=CandidateOutcome(
            name="高血压",
            data_type="binary",
            definition=(
                "按研究者确认的现场平均血压阈值"
                "和当前降压药使用状态构造二分类高血压结局。"
            ),
            sensitivity_definitions=[
                "替代高血压阈值定义",
            ],
        ),
        covariates=[
            CandidateCovariate(
                name="年龄"
            ),
            CandidateCovariate(
                name="性别"
            ),
            CandidateCovariate(
                name="BMI"
            ),
        ],
        missing_data=CandidateMissingData(
            strategy=missing_strategy,
            mode=(
                "fixed"
                if missing_strategy
                in {
                    "complete_case_global",
                    "multiple_imputation",
                }
                else "data_dependent"
            ),
            assessment=[
                "缺失比例",
                "缺失模式",
            ],
            decision_rule=(
                "根据数据质量评估决定主策略"
            ),
            sensitivity_plan=(
                "比较不同缺失值处理结果"
            ),
        ),
        analysis=CandidateAnalysis(
            method=analysis_method,
            effect_measure="OR",
            ci_level=0.95,
            survey_design_required=True,
            secondary_analyses=[
                "restricted_cubic_spline",
            ],
            sensitivity_analyses=[
                "robust_poisson_pr",
            ],
        ),
    )

    candidate.open_issues = (
        CandidateSpecValidator
        .validate(candidate)
    )

    return candidate


print()
print("========================================")
print("Conversational Planning V0.3 验收")
print("========================================")


candidate = build_complete_candidate()


print()
print("1. 确定性 readiness")

assert (
    ConversationalReadinessV03
    .is_ready(candidate)
)

assert (
    ConversationalReadinessV03
    .missing_fields(candidate)
    == []
)

print(
    "PASS：完整研究状态可进入冻结阶段"
)


print()
print("2. 已确认字段禁止重复成为讨论目标")

partial_data = (
    candidate.model_dump()
)

partial_data[
    "outcome"
][
    "definition"
] = None

partial_data[
    "missing_data"
][
    "strategy"
] = None

partial_data[
    "analysis"
][
    "method"
] = None

partial = (
    CandidateResearchSpecV01
    .model_validate(
        partial_data
    )
)

partial.open_issues = (
    CandidateSpecValidator
    .validate(partial)
)

targets = (
    ConversationalReadinessV03
    .discussion_targets(
        partial,
        confirmed_fields=[
            "study_design",
            "dataset.name",
            "population.age_min",
            "exposure.name",
            "exposure.data_type",
            "exposure.analysis_form",
            "outcome.name",
            "outcome.data_type",
        ],
    )
)

assert (
    "exposure.analysis_form"
    not in targets
)

assert targets == [
    "outcome.definition",
    "missing_data.strategy",
    "analysis.method",
]

print(
    "PASS：已确认的暴露分析形式不会被再次主动询问"
)

print()
print("2.4 NHANES 周期缺失时禁止冻结")

missing_cycle = build_complete_candidate()

missing_cycle_data = (
    missing_cycle.model_dump()
)

missing_cycle_data[
    "dataset"
][
    "version"
] = None

missing_cycle = (
    CandidateResearchSpecV01
    .model_validate(
        missing_cycle_data
    )
)

missing_cycle.open_issues = (
    CandidateSpecValidator
    .validate(missing_cycle)
)

assert (
    ConversationalReadinessV03
    .is_ready(missing_cycle)
    is False
)

assert (
    "dataset.version"
    in (
        ConversationalReadinessV03
        .missing_fields(
            missing_cycle
        )
    )
)

assert any(
    issue.field_path
    == "dataset.version"
    and issue.blocking
    for issue in (
        missing_cycle.open_issues
    )
)

print(
    "PASS：NHANES 调查周期未确定时不能 READY_TO_FREEZE"
)


print()
print("2.5 冻结命令必须由系统路由")

assert (
    PlanningCommandRouterV03
    .route("冻结")
    == "FREEZE"
)

assert (
    PlanningCommandRouterV03
    .route("冻结方案")
    == "FREEZE"
)

assert (
    PlanningCommandRouterV03
    .route("请冻结方案")
    == "FREEZE"
)

print(
    "PASS：冻结类命令不会再进入普通 LLM 对话"
)


print()
print("2.6 多变量模型但协变量为空时禁止冻结")

no_covariate = (
    build_complete_candidate()
)

no_covariate_data = (
    no_covariate.model_dump()
)

no_covariate_data[
    "covariates"
] = []

no_covariate_data[
    "analysis"
][
    "method"
] = (
    "survey-weighted multivariable logistic regression"
)

no_covariate = (
    CandidateResearchSpecV01
    .model_validate(
        no_covariate_data
    )
)

no_covariate.open_issues = (
    CandidateSpecValidator
    .validate(no_covariate)
)

assert (
    ConversationalReadinessV03
    .is_ready(no_covariate)
    is False
)

assert any(
    "协变量框架仍为空"
    in reason
    for reason in (
        ConversationalReadinessV03
        .blocking_reasons(
            no_covariate
        )
    )
)

print(
    "PASS：多变量模型 + 空协变量不会再 READY_TO_FREEZE"
)


print()
print("3. 人类可读方案预览")

confirmed_fields = [
    "study_design",
    "objective",
    "dataset.name",
    "population.age_min",
    "exposure.name",
    "exposure.data_type",
    "exposure.analysis_form",
    "outcome.name",
    "outcome.data_type",
    "outcome.definition",
    "covariates",
    "missing_data.strategy",
    "analysis.method",
]

preview = (
    ResearchPlanPreviewV03
    .render(
        candidate,
        confirmed_fields,
    )
)

assert "研究方案实时预览" in preview
assert "25-羟基维生素D" in preview

print(
    "PASS：可以从结构化状态生成方案预览"
)


print()
print("4. 构造对话会话")

now = datetime.now(
    timezone.utc
)

session = PlanningSessionV03(
    session_id="PS-TEST-V03",
    status="READY_TO_FREEZE",
    messages=[
        PlanningMessageV03(
            role="user",
            content=(
                "我想研究维生素D和高血压的关系。"
            ),
            created_at=now,
        ),
        PlanningMessageV03(
            role="assistant",
            content=(
                "可以，我们逐步把研究方案讨论清楚。"
            ),
            created_at=now,
        ),
    ],
    current_candidate=candidate,
    confirmed_fields=confirmed_fields,
    decisions=[
        PlanningDecisionV03(
            field_path="dataset.name",
            value="NHANES",
            evidence="使用 NHANES",
            decided_at=now,
        ),
        PlanningDecisionV03(
            field_path="population.age_min",
            value=20,
            evidence="20岁以上",
            decided_at=now,
        ),
    ],
    pending_suggestions=[],
    created_at=now,
    updated_at=now,
)

print(
    "PASS：Planning Session 可保存消息、状态和人工决策"
)


print()
print("5. 确定性冻结")

(
    frozen_session,
    review_log,
    frozen_plan,
) = (
    ConversationalPlanningFinalizerV03
    .finalize(
        session=session,
        reviewed_by="test_user",
    )
)

assert (
    frozen_session.status
    == "FROZEN"
)

assert (
    frozen_plan.status
    == "FROZEN"
)

assert (
    review_log.status
    == "COMPLETE"
)

assert (
    frozen_plan
    .research_plan
    .analysis
    .primary_model
    == "logistic_regression"
)

assert (
    frozen_plan
    .research_plan
    .analysis
    .effect_measure
    == "OR"
)

assert (
    frozen_plan
    .research_plan
    .analysis
    .ci_level
    == 0.95
)

assert (
    frozen_plan
    .research_plan
    .analysis
    .survey_design_required
    is True
)

assert (
    "restricted_cubic_spline"
    in frozen_plan
    .research_plan
    .analysis
    .secondary_analyses
)

assert (
    "robust_poisson_pr"
    in frozen_plan
    .research_plan
    .analysis
    .sensitivity_analyses
)

assert (
    "替代高血压阈值定义"
    in frozen_plan
    .research_plan
    .outcome
    .sensitivity_definitions
)

assert (
    frozen_plan
    .research_plan
    .missing_data
    .assessment
    == [
        "缺失比例",
        "缺失模式",
    ]
)

print(
    "PASS：Rich Research Plan 冻结时不会丢失"
    "效应量、CI、复杂抽样、次要/敏感性分析和缺失策略细节"
)


print()
print("6. Research Plan 与当前执行能力分离")

unsupported_candidate = (
    build_complete_candidate(
        missing_strategy=(
            "multiple_imputation"
        )
    )
)

unsupported_session = (
    session.model_copy(
        update={
            "status": "READY_TO_FREEZE",
            "current_candidate": (
                unsupported_candidate
            ),
        }
    )
)

(
    _,
    _,
    unsupported_frozen,
) = (
    ConversationalPlanningFinalizerV03
    .finalize(
        session=unsupported_session,
        reviewed_by="test_user",
    )
)

capability = (
    ExecutionCapabilityCheckerV03
    .check(
        unsupported_frozen
        .research_plan
    )
)

assert (
    unsupported_frozen
    .research_plan
    .missing_data
    .strategy
    == "multiple_imputation"
)

assert capability.supported is False

assert any(
    "multiple_imputation"
    in reason
    for reason in (
        capability
        .unsupported_reasons
    )
)

print(
    "PASS：科研方案可以冻结多重插补，"
    "执行能力检查再单独报告当前尚未实现"
)


print()
print("7. 保存完整审计产物")

with tempfile.TemporaryDirectory() as tmp:

    store = (
        ConversationPlanningStoreV03(
            Path(tmp)
        )
    )

    output_dir = (
        store.save_final_bundle(
            session=frozen_session,
            review_log=review_log,
            frozen_plan=frozen_plan,
        )
    )

    assert (
        output_dir
        / "planning_session.json"
    ).exists()

    assert (
        output_dir
        / "transcript.json"
    ).exists()

    assert (
        output_dir
        / "review_log.json"
    ).exists()

    assert (
        output_dir
        / "research_plan.json"
    ).exists()

print(
    "PASS：会话、聊天记录、审核日志和 Research Plan 已分离保存"
)


print()
print("8. 不完整方案禁止冻结")

incomplete = build_complete_candidate()

incomplete_data = (
    incomplete.model_dump()
)

incomplete_data[
    "analysis"
][
    "method"
] = None

incomplete = (
    CandidateResearchSpecV01
    .model_validate(
        incomplete_data
    )
)

incomplete.open_issues = (
    CandidateSpecValidator
    .validate(incomplete)
)

incomplete_session = (
    session.model_copy(
        update={
            "status": "DISCUSSING",
            "current_candidate": incomplete,
        }
    )
)

try:

    ConversationalPlanningFinalizerV03.finalize(
        session=incomplete_session,
        reviewed_by="test_user",
    )

    raise AssertionError(
        "不完整 Research Plan 竟然被冻结"
    )

except ValueError:

    print(
        "PASS：不完整方案无法冻结"
    )


print()
print("========================================")
print("Conversational Planning V0.3 验收完成")
print("========================================")
