import json
import sys
from pathlib import Path


# ==========================================
# 项目路径初始化
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
    CandidateReadiness,
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
# 输出 JSON
# ==========================================

def print_json(obj):

    print(
        json.dumps(
            obj.model_dump(
                mode="json"
            ),
            ensure_ascii=False,
            indent=2,
        )
    )


# ==========================================
# Yes / No
# ==========================================

def ask_yes_no(
    question: str,
) -> bool:

    while True:

        value = input(
            f"{question} [y/n]："
        ).strip().lower()

        if value in {
            "y",
            "yes",
        }:
            return True

        if value in {
            "n",
            "no",
        }:
            return False

        print(
            "请输入 y 或 n。"
        )


# ==========================================
# 根据 open issue 询问用户
# ==========================================

def ask_issue(issue):

    path = issue.field_path

    print()
    print("----------------------------------------")
    print(issue.question)

    if not issue.blocking:
        print(
            "（该项不是强制项，可直接回车跳过）"
        )

    # ======================================
    # Study Design
    # ======================================

    if path == "study_design":

        if ask_yes_no(
            "本研究是否为横断面研究？"
        ):

            return "cross_sectional"

        print()
        print(
            "当前 V0.1 只支持横断面研究。"
        )

        return None

    # ======================================
    # Dataset
    # ======================================

    if path == "dataset.name":

        value = input(
            "请输入数据集名称，例如 NHANES："
        ).strip()

        return (
            value
            if value
            else None
        )

    # ======================================
    # Population
    # ======================================

    if path == "population.age_min":

        while True:

            value = input(
                "请输入最低年龄，例如 20："
            ).strip()

            if not value:
                return None

            try:
                return float(
                    value
                )

            except ValueError:
                print(
                    "年龄必须输入数字。"
                )

    # ======================================
    # Exposure Data Type
    # ======================================

    if path == "exposure.data_type":

        while True:

            print()
            print(
                "1 = continuous 连续变量"
            )
            print(
                "2 = categorical 分类变量"
            )
            print(
                "3 = binary 二分类变量"
            )

            choice = input(
                "请选择："
            ).strip()

            mapping = {
                "1": "continuous",
                "2": "categorical",
                "3": "binary",
            }

            if choice in mapping:
                return mapping[
                    choice
                ]

            print(
                "无效选择。"
            )

    # ======================================
    # Exposure Analysis Form
    # ======================================

    if path == "exposure.analysis_form":

        while True:

            print()
            print(
                "1 = continuous 连续形式"
            )
            print(
                "2 = categorical 分类形式"
            )

            choice = input(
                "请选择："
            ).strip()

            mapping = {
                "1": "continuous",
                "2": "categorical",
            }

            if choice in mapping:
                return mapping[
                    choice
                ]

            print(
                "无效选择。"
            )

    # ======================================
    # Exposure Unit
    # ======================================

    if path == "exposure.unit":

        value = input(
            "请输入暴露变量单位；"
            "不知道可直接回车："
        ).strip()

        return (
            value
            if value
            else None
        )

    # ======================================
    # Outcome Data Type
    # ======================================

    if path == "outcome.data_type":

        if ask_yes_no(
            "结局是否为二分类变量？"
        ):

            return "binary"

        print()
        print(
            "当前 V0.1 只支持二分类结局。"
        )

        return None

    # ======================================
    # Outcome Definition
    # ======================================

    if path == "outcome.definition":

        value = input(
            "请输入明确的结局定义或判定标准：\n> "
        ).strip()

        return (
            value
            if value
            else None
        )

    # ======================================
    # Analysis Method
    # ======================================

    if path == "analysis.method":

        while True:

            print()
            print(
                "当前 V0.1 支持："
            )
            print(
                "1 = Logistic 回归"
            )

            choice = input(
                "请选择主分析方法："
            ).strip()

            if choice == "1":

                return (
                    "logistic_regression"
                )

            print(
                "无效选择。"
            )

    # ======================================
    # Missing Data
    # ======================================

    if path == "missing_data.strategy":

        if ask_yes_no(
            "是否采用完整病例分析 "
            "（Complete Case Analysis）？"
        ):

            return (
                "complete_case_global"
            )

        print()
        print(
            "当前 V0.1 暂时只支持"
            "完整病例分析。"
        )

        return None

    # ======================================
    # Fallback
    # ======================================

    value = input(
        f"请输入 {path}："
    ).strip()

    return (
        value
        if value
        else None
    )


# ==========================================
# 人工修改 Research Spec
# ==========================================

def edit_candidate_interactively(
    candidate,
):

    while True:

        print()
        print("========================================")
        print("请选择需要修改的内容")
        print("========================================")
        print()
        print("1. 研究设计")
        print("2. 数据集名称")
        print("3. 最低年龄")
        print("4. 暴露变量名称")
        print("5. 暴露变量类型")
        print("6. 暴露分析形式")
        print("7. 暴露变量单位")
        print("8. 结局变量名称")
        print("9. 结局变量类型")
        print("10. 结局定义")
        print("11. 协变量")
        print("12. 缺失值处理策略")
        print("13. 主分析方法")
        print("0. 完成修改")

        choice = input(
            "\n请选择："
        ).strip()

        if choice == "0":

            return candidate

        answers = {}

        # ======================================
        # 1 Study Design
        # ======================================

        if choice == "1":

            print()
            print(
                "当前 V0.1 仅支持："
            )
            print(
                "1 = cross_sectional 横断面研究"
            )

            value = input(
                "请选择："
            ).strip()

            if value != "1":

                print(
                    "无效选择。"
                )

                continue

            answers[
                "study_design"
            ] = "cross_sectional"

        # ======================================
        # 2 Dataset
        # ======================================

        elif choice == "2":

            value = input(
                "请输入数据集名称："
            ).strip()

            if not value:

                print(
                    "数据集名称不能为空。"
                )

                continue

            answers[
                "dataset.name"
            ] = value

        # ======================================
        # 3 Age
        # ======================================

        elif choice == "3":

            value = input(
                "请输入最低年龄："
            ).strip()

            try:

                answers[
                    "population.age_min"
                ] = float(
                    value
                )

            except ValueError:

                print(
                    "年龄必须是数字。"
                )

                continue

        # ======================================
        # 4 Exposure Name
        # ======================================

        elif choice == "4":

            value = input(
                "请输入暴露变量名称："
            ).strip()

            if not value:

                print(
                    "暴露变量名称不能为空。"
                )

                continue

            answers[
                "exposure.name"
            ] = value

        # ======================================
        # 5 Exposure Data Type
        # ======================================

        elif choice == "5":

            print()
            print(
                "1 = continuous"
            )
            print(
                "2 = categorical"
            )
            print(
                "3 = binary"
            )

            value = input(
                "请选择："
            ).strip()

            mapping = {
                "1": "continuous",
                "2": "categorical",
                "3": "binary",
            }

            if value not in mapping:

                print(
                    "无效选择。"
                )

                continue

            answers[
                "exposure.data_type"
            ] = mapping[
                value
            ]

        # ======================================
        # 6 Analysis Form
        # ======================================

        elif choice == "6":

            print()
            print(
                "1 = continuous"
            )
            print(
                "2 = categorical"
            )

            value = input(
                "请选择："
            ).strip()

            mapping = {
                "1": "continuous",
                "2": "categorical",
            }

            if value not in mapping:

                print(
                    "无效选择。"
                )

                continue

            answers[
                "exposure.analysis_form"
            ] = mapping[
                value
            ]

        # ======================================
        # 7 Exposure Unit
        # ======================================

        elif choice == "7":

            value = input(
                "请输入暴露变量单位："
            ).strip()

            answers[
                "exposure.unit"
            ] = (
                value
                if value
                else None
            )

        # ======================================
        # 8 Outcome Name
        # ======================================

        elif choice == "8":

            value = input(
                "请输入结局变量名称："
            ).strip()

            if not value:

                print(
                    "结局变量名称不能为空。"
                )

                continue

            answers[
                "outcome.name"
            ] = value

        # ======================================
        # 9 Outcome Type
        # ======================================

        elif choice == "9":

            if ask_yes_no(
                "是否设为 binary 二分类结局？"
            ):

                answers[
                    "outcome.data_type"
                ] = "binary"

            else:

                print(
                    "当前 V0.1 只支持 binary。"
                )

                continue

        # ======================================
        # 10 Outcome Definition
        # ======================================

        elif choice == "10":

            value = input(
                "请输入明确的结局定义：\n> "
            ).strip()

            if not value:

                print(
                    "结局定义不能为空。"
                )

                continue

            answers[
                "outcome.definition"
            ] = value

        # ======================================
        # 11 Covariates
        # ======================================

        elif choice == "11":

            value = input(
                "请输入协变量，"
                "多个变量用英文逗号分隔：\n> "
            ).strip()

            if not value:

                new_covariates = []

            else:

                names = [
                    item.strip()
                    for item in (
                        value.split(",")
                    )
                    if item.strip()
                ]

                new_covariates = [
                    {
                        "name": name,
                        "column": None,
                        "data_type": None,
                        "unit": None,
                        "reference_value": None,
                    }
                    for name in names
                ]

            answers[
                "covariates"
            ] = new_covariates

        # ======================================
        # 12 Missing Data
        # ======================================

        elif choice == "12":

            if ask_yes_no(
                "是否采用完整病例分析？"
            ):

                answers[
                    "missing_data.strategy"
                ] = (
                    "complete_case_global"
                )

            else:

                print(
                    "当前 V0.1 暂时只支持完整病例分析。"
                )

                continue

        # ======================================
        # 13 Analysis Method
        # ======================================

        elif choice == "13":

            print()
            print(
                "当前 V0.1 支持："
            )
            print(
                "1 = Logistic 回归"
            )

            value = input(
                "请选择："
            ).strip()

            if value != "1":

                print(
                    "无效选择。"
                )

                continue

            answers[
                "analysis.method"
            ] = (
                "logistic_regression"
            )

        else:

            print(
                "无效选择。"
            )

            continue

        candidate = (
            CandidateSpecUpdater
            .apply_answers(
                spec=candidate,
                answers=answers,
            )
        )

        print()
        print(
            "修改已保存。"
        )


# ==========================================
# 启动 Demo
# ==========================================

print()
print("========================================")
print(" 医学数据分析工作流平台 V0.1")
print(" Research Spec Demo")
print("========================================")
print()


# ==========================================
# 1. 输入研究问题
# ==========================================

question = input(
    "请输入研究问题：\n> "
).strip()

if not question:

    raise RuntimeError(
        "研究问题不能为空。"
    )


# ==========================================
# 2. DeepSeek 整理
# ==========================================

print()
print(
    "正在调用 DeepSeek 整理研究条件……"
)

generator = (
    ResearchSpecGenerator()
)

candidate = (
    generator.generate(
        question
    )
)

print()
print("========================================")
print("AI 初步整理结果")
print("========================================")
print()

print_json(
    candidate
)


# ==========================================
# 3. 自动发现缺失信息
# ==========================================

while True:

    status = (
        CandidateReadinessChecker
        .check(
            candidate
        )
    )

    if (
        status
        == CandidateReadiness.READY_FOR_REVIEW
    ):

        break

    print()
    print("========================================")
    print("当前方案需要补充以下信息")
    print("========================================")

    answers = {}

    for issue in (
        candidate.open_issues
    ):

        value = ask_issue(
            issue
        )

        if value is not None:

            answers[
                issue.field_path
            ] = value

    if not answers:

        print()
        print(
            "没有补充任何有效信息。"
        )
        print(
            "当前方案仍无法进入人工审核。"
        )

        sys.exit(1)

    candidate = (
        CandidateSpecUpdater
        .apply_answers(
            spec=candidate,
            answers=answers,
        )
    )


# ==========================================
# 4. 人工审核 / 修改循环
# ==========================================

while True:

    print()
    print("========================================")
    print("当前待确认 Research Spec")
    print("========================================")
    print()

    print_json(
        candidate
    )

    status = (
        CandidateReadinessChecker
        .check(
            candidate
        )
    )

    # --------------------------------------
    # 修改之后如果又出现 blocking issue
    # --------------------------------------

    if (
        status
        != CandidateReadiness.READY_FOR_REVIEW
    ):

        print()
        print(
            "修改后的方案存在必须补充的信息。"
        )

        answers = {}

        for issue in (
            candidate.open_issues
        ):

            if not issue.blocking:
                continue

            value = ask_issue(
                issue
            )

            if value is not None:

                answers[
                    issue.field_path
                ] = value

        if answers:

            candidate = (
                CandidateSpecUpdater
                .apply_answers(
                    spec=candidate,
                    answers=answers,
                )
            )

        continue

    # --------------------------------------
    # 最终确认
    # --------------------------------------

    confirmed = ask_yes_no(
        "请检查以上分析方案，是否确认？"
    )

    if confirmed:

        print()
        print(
            "研究方案已人工确认。"
        )

        break

    # --------------------------------------
    # 不确认
    # --------------------------------------

    print()
    print(
        "当前 Research Spec 未确认。"
    )
    print()
    print(
        "1. 返回修改研究方案"
    )
    print(
        "2. 放弃本次研究方案"
    )

    action = input(
        "请选择："
    ).strip()

    if action == "1":

        candidate = (
            edit_candidate_interactively(
                candidate
            )
        )

        continue

    if action == "2":

        print()
        print(
            "本次研究方案已放弃。"
        )
        print(
            "不会生成 Frozen Research Spec。"
        )

        sys.exit(0)

    print()
    print(
        "无效选择，将重新显示 Research Spec。"
    )


# ==========================================
# 5. 人工确认记录
# ==========================================

reviewed_spec = (
    SpecReviewService.confirm(
        spec=candidate,
        confirmed_by="demo_user",
    )
)


# ==========================================
# 6. 冻结
# ==========================================

frozen_spec = (
    SpecFreezeService.freeze(
        reviewed_spec
    )
)


# ==========================================
# 7. 保存
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


# ==========================================
# 8. 最终输出
# ==========================================

print()
print("========================================")
print("分析方案已正式冻结")
print("========================================")
print()

print(
    f"Spec ID："
    f"{frozen_spec.spec_id}"
)

print(
    f"版本："
    f"V{frozen_spec.spec_version}"
)

print(
    f"状态："
    f"{frozen_spec.status}"
)

print(
    f"Content Hash："
    f"{frozen_spec.content_hash}"
)

print()
print(
    "保存位置："
)

print(
    saved_path
)

print()
print("========================================")
print("Research Spec V0.1 流程完成")
print("========================================")