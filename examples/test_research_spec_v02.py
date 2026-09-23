import json
import sys
import tempfile
from pathlib import Path

from pydantic import ValidationError


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
from medflow.planning.proposal_builder import (
    ProposalBuilderV02,
)
from medflow.planning.review_engine import (
    ReviewEngineV02,
)
from medflow.planning.research_plan_builder import (
    ResearchPlanBuilderV02,
)
from medflow.planning.freeze_service_v02 import (
    ResearchPlanFreezeServiceV02,
)
from medflow.planning.store_v02 import (
    ResearchPlanningStoreV02,
)
from medflow.spec.candidate_validator import (
    CandidateSpecValidator,
)


def build_candidate():
    candidate = CandidateResearchSpecV01(
        source_question=(
            "基于 NHANES 开展横断面研究，"
            "纳入20岁及以上成年人，"
            "研究血清维生素D与高血压的关联，"
            "调整年龄、性别和BMI。"
        ),
        study_design="cross_sectional",
        objective="association",
        dataset=CandidateDataset(
            name="NHANES",
        ),
        population=CandidatePopulation(
            age_min=20,
        ),
        exposure=CandidateExposure(
            name="血清25-羟基维生素D",
            data_type="continuous",
            unit="ng/mL",
            analysis_form="continuous",
        ),
        outcome=CandidateOutcome(
            name="高血压",
            data_type="binary",
            definition=(
                "按预先确认的研究判定规则构造二分类高血压结局。"
            ),
        ),
        covariates=[
            CandidateCovariate(name="年龄"),
            CandidateCovariate(name="性别"),
            CandidateCovariate(name="BMI"),
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
print("Research Planning V0.2 验收")
print("========================================")


candidate = build_candidate()

print()
print("1. 构建 Candidate Proposal")

proposal = (
    ProposalBuilderV02
    .build(candidate)
)

assert proposal.schema_version == "0.2.0"
assert len(proposal.items) > 0

print("PASS：Candidate Proposal 已生成")


print()
print("2. Generic Review Engine")

reviewed_candidate, review_log = (
    ReviewEngineV02
    .apply(
        proposal=proposal,
        selections={
            "covariates": [
                "年龄",
                "性别",
                "BMI",
            ]
        },
        reviewed_by="test_reviewer",
    )
)

assert review_log.status == "COMPLETE"
assert review_log.reviewed_by == "test_reviewer"

print("PASS：人工决策已独立记录")


print()
print("3. 构建正式 Research Plan")

research_plan = (
    ResearchPlanBuilderV02
    .build(
        reviewed_candidate=reviewed_candidate,
        review_log=review_log,
    )
)

assert research_plan.study_design == "cross_sectional"
assert research_plan.analysis.method == "logistic_regression"
assert research_plan.dataset.name == "NHANES"
assert research_plan.exposure.preferred_unit == "ng/mL"

plan_json = (
    research_plan
    .model_dump(
        mode="json"
    )
)

assert "open_issues" not in plan_json
assert "review_status" not in plan_json
assert "column" not in plan_json["exposure"]
assert "column" not in plan_json["outcome"]

print(
    "PASS：正式 Research Plan 与 Proposal / "
    "真实数据列绑定已分离"
)


print()
print("4. 冻结 Research Plan")

frozen = (
    ResearchPlanFreezeServiceV02
    .freeze(
        research_plan=research_plan,
        review_log=review_log,
    )
)

assert frozen.status == "FROZEN"
assert frozen.review_id == review_log.review_id

print("PASS：Research Plan 已冻结")


print()
print("5. Hash 稳定性")

frozen_2 = (
    ResearchPlanFreezeServiceV02
    .freeze(
        research_plan=research_plan,
        review_log=review_log,
    )
)

assert (
    frozen.content_hash
    == frozen_2.content_hash
)

print(
    "PASS：相同 Research Plan 产生相同 content_hash"
)


print()
print("6. Frozen 不可直接修改")

try:

    frozen.plan_version = 2

    raise AssertionError(
        "FrozenResearchPlanV02 可以被直接修改"
    )

except ValidationError:

    print(
        "PASS：Frozen Research Plan 已阻止直接修改"
    )


print()
print("7. 模糊语义禁止进入正式 Research Plan")

fuzzy_candidate = build_candidate()

fuzzy_data = (
    fuzzy_candidate
    .model_dump()
)

fuzzy_data[
    "outcome"
][
    "definition"
] = (
    "待确认：可采用140/90或130/80，视情况而定。"
)

fuzzy_candidate = (
    CandidateResearchSpecV01
    .model_validate(
        fuzzy_data
    )
)

fuzzy_candidate.open_issues = (
    CandidateSpecValidator
    .validate(
        fuzzy_candidate
    )
)

fuzzy_proposal = (
    ProposalBuilderV02
    .build(
        fuzzy_candidate
    )
)

fuzzy_reviewed, fuzzy_log = (
    ReviewEngineV02
    .apply(
        proposal=fuzzy_proposal,
        selections={},
        reviewed_by="test_reviewer",
    )
)

try:

    ResearchPlanBuilderV02.build(
        reviewed_candidate=fuzzy_reviewed,
        review_log=fuzzy_log,
    )

    raise AssertionError(
        "模糊语义竟然进入了 Research Plan"
    )

except ValueError as exc:

    assert "模糊表述" in str(exc)

    print(
        "PASS：待确认/视情况等模糊语义已被阻止"
    )


print()
print("8. Bundle Store")

with tempfile.TemporaryDirectory() as tmp:

    store = (
        ResearchPlanningStoreV02(
            Path(tmp)
        )
    )

    saved_dir = (
        store.save_bundle(
            proposal=proposal,
            review_log=review_log,
            frozen_plan=frozen,
        )
    )

    assert (
        saved_dir
        / "proposal.json"
    ).exists()

    assert (
        saved_dir
        / "review_log.json"
    ).exists()

    assert (
        saved_dir
        / "research_plan.json"
    ).exists()

    print(
        "PASS：Proposal / Review Log / Research Plan "
        "已分开保存"
    )


print()
print("========================================")
print("Research Planning V0.2 验收完成")
print("========================================")
print()

print(
    json.dumps(
        frozen.model_dump(
            mode="json"
        ),
        ensure_ascii=False,
        indent=2,
    )
)
