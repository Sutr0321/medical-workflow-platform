import json
import sys
from pathlib import Path


# ==========================================
# 项目路径
# ==========================================

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


# ==========================================
# 项目模块
# ==========================================

from medflow.llm.spec_generator import (
    ResearchSpecGenerator,
)

from medflow.spec.candidate_updater import (
    CandidateSpecUpdater,
)

from medflow.spec.readiness import (
    CandidateReadinessChecker,
)

from medflow.spec.review_service import (
    SpecReviewService,
)

from medflow.spec.freeze_service import (
    SpecFreezeService,
)

from medflow.spec.store import (
    FrozenSpecStore,
)


# ==========================================
# 1. 用户研究问题
# ==========================================

question = """
我想研究成年人中 Vitamin D 水平与高血压之间的关系，
并调整年龄、性别和 BMI。
"""


# ==========================================
# 2. DeepSeek 第一次提取
# ==========================================

generator = (
    ResearchSpecGenerator()
)

candidate = (
    generator.generate(
        question
    )
)

first_status = (
    CandidateReadinessChecker
    .check(
        candidate
    )
)

print()
print("==============================")
print("第一次 Candidate 状态")
print("==============================")
print()

print(
    first_status.value
)

print(
    json.dumps(
        candidate.model_dump(
            mode="json"
        ),
        ensure_ascii=False,
        indent=2,
    )
)


# ==========================================
# 3. 模拟科研人员补充条件
# ==========================================

answers = {

    "study_design":
        "cross_sectional",

    "dataset.name":
        "NHANES",

    "population.age_min":
        20,

    "exposure.data_type":
        "continuous",

    "exposure.analysis_form":
        "continuous",

    "exposure.unit":
        "ng/mL",

    "outcome.data_type":
        "binary",

    "outcome.definition":
        (
            "本测试中 hypertension=1 "
            "表示高血压，0 表示无高血压；"
            "仅用于程序流程测试。"
        ),

    "analysis.method":
        "logistic_regression",

    "missing_data.strategy":
        "complete_case_global",
}


# ==========================================
# 4. 固定程序更新 Candidate
# ==========================================

updated_candidate = (
    CandidateSpecUpdater
    .apply_answers(
        spec=candidate,
        answers=answers,
    )
)

updated_status = (
    CandidateReadinessChecker
    .check(
        updated_candidate
    )
)

print()
print("==============================")
print("补充后的 Candidate 状态")
print("==============================")
print()

print(
    updated_status.value
)

print(
    json.dumps(
        updated_candidate.model_dump(
            mode="json"
        ),
        ensure_ascii=False,
        indent=2,
    )
)


# ==========================================
# 5. 显示剩余问题
# ==========================================

print()
print("==============================")
print("剩余 open issues")
print("==============================")
print()

for issue in (
    updated_candidate.open_issues
):

    print(
        f"{issue.issue_id} | "
        f"{issue.field_path} | "
        f"blocking={issue.blocking} | "
        f"{issue.question}"
    )


# ==========================================
# 6. 人工确认 Research Spec
# ==========================================

print()
print("==============================")
print("人工确认研究方案")
print("==============================")
print()

reviewed_spec = (
    SpecReviewService.confirm(
        spec=updated_candidate,
        confirmed_by="test_user",
    )
)

print(
    json.dumps(
        reviewed_spec.model_dump(
            mode="json"
        ),
        ensure_ascii=False,
        indent=2,
    )
)

print()
print("==============================")
print("人工确认后的状态")
print("==============================")
print()

print(
    reviewed_spec.review_status
)


# ==========================================
# 7. 冻结 Research Spec
# ==========================================

print()
print("==============================")
print("冻结 Research Spec")
print("==============================")
print()

frozen_spec = (
    SpecFreezeService.freeze(
        reviewed_spec
    )
)

print(
    json.dumps(
        frozen_spec.model_dump(
            mode="json"
        ),
        ensure_ascii=False,
        indent=2,
    )
)


# ==========================================
# 8. 保存 Frozen Spec
# ==========================================

store = FrozenSpecStore(
    project_root
    / "artifacts"
    / "specs"
)

saved_path = (
    store.save(
        frozen_spec
    )
)

print()
print("==============================")
print("Frozen Research Spec 已保存")
print("==============================")
print()

print(
    saved_path
)


# ==========================================
# 9. 不完整方案禁止确认
# ==========================================

print()
print("==============================")
print("测试不完整方案是否能被错误确认")
print("==============================")
print()

try:

    SpecReviewService.confirm(
        spec=candidate,
        confirmed_by="test_user",
    )

    print(
        "ERROR：不完整方案竟然被确认了"
    )

except ValueError as exc:

    print(
        "PASS：不完整方案已被系统阻止"
    )

    print(
        str(exc)
    )


# ==========================================
# 10. Hash 稳定性
# ==========================================

print()
print("==============================")
print("测试 Research Spec Hash 稳定性")
print("==============================")
print()

frozen_spec_2 = (
    SpecFreezeService.freeze(
        reviewed_spec
    )
)

if (
    frozen_spec.content_hash
    == frozen_spec_2.content_hash
):

    print(
        "PASS：相同研究方案生成相同 content_hash"
    )

else:

    print(
        "ERROR：相同研究方案的 content_hash 不一致"
    )


# ==========================================
# 11. Frozen Spec 不可直接修改
# ==========================================

print()
print("==============================")
print("测试 Frozen Research Spec 不可修改")
print("==============================")
print()

try:

    frozen_spec.spec_version = 2

    print(
        "ERROR：Frozen Research Spec 竟然可以直接修改"
    )

except Exception as exc:

    print(
        "PASS：Frozen Research Spec 已阻止直接修改"
    )

    print(
        type(exc).__name__
    )


# ==========================================
# 12. Frozen V1 禁止覆盖
# ==========================================

print()
print("==============================")
print("测试 Frozen V1 是否禁止覆盖")
print("==============================")
print()

try:

    store.save(
        frozen_spec
    )

    print(
        "ERROR：已有 Frozen V1 竟然被允许覆盖"
    )

except FileExistsError as exc:

    print(
        "PASS：已有 Frozen V1 已被系统阻止覆盖"
    )

    print(
        str(exc)
    )


print()
print("==============================")
print("Research Spec Engine V0.1 验收完成")
print("==============================")