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
from medflow.spec.candidate_validator import (
    CandidateSpecValidator,
)


def build_complete_candidate():

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
            unit="待 Data Binding 核对",
            analysis_form="continuous",
        ),
        outcome=CandidateOutcome(
            name="高血压",
            data_type="binary",
            definition=(
                "采用研究者最终确认的二分类高血压定义；"
                "真实变量和派生规则在 Data Binding 阶段核对。"
            ),
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
            strategy="complete_case_global"
        ),
        analysis=CandidateAnalysis(
            method="logistic_regression"
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
print("2. 人类可读方案预览")

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
assert "Logistic" not in preview or "logistic_regression" in preview

print(
    "PASS：可以从结构化状态生成前端式方案预览"
)


print()
print("3. 构造对话会话")

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
                "可以，我们逐步把研究设计讨论清楚。"
            ),
            created_at=now,
        ),
        PlanningMessageV03(
            role="user",
            content=(
                "用NHANES 2017-2018，20岁以上，"
                "横断面，主分析用Logistic。"
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
            evidence=(
                "用NHANES 2017-2018"
            ),
            decided_at=now,
        ),
        PlanningDecisionV03(
            field_path="population.age_min",
            value=20,
            evidence="20岁以上",
            decided_at=now,
        ),
        PlanningDecisionV03(
            field_path="analysis.method",
            value="logistic_regression",
            evidence="主分析用Logistic",
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
print("4. 确定性冻结")

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
    frozen_plan
    .research_plan
    .analysis
    .method
    == "logistic_regression"
)

assert (
    review_log.status
    == "COMPLETE"
)

print(
    "PASS：对话完成后可确定性生成 Frozen Research Plan"
)


print()
print("5. 保存完整审计产物")

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
print("6. 不完整方案禁止冻结")

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
