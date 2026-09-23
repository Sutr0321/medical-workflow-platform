import json
import sys
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


from medflow.llm.spec_generator import (
    ResearchSpecGenerator,
)
from medflow.planning.proposal_builder import (
    ProposalBuilderV02,
)
from medflow.planning.review_engine import (
    ReviewEngineV02,
)
from medflow.planning.execution_builder import (
    ExecutionSpecBuilderV02,
)
from medflow.planning.freeze_service_v02 import (
    ExecutionSpecFreezeServiceV02,
)
from medflow.planning.store_v02 import (
    ResearchPlanningStoreV02,
)


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


def parse_custom_value(
    field_path: str,
    raw: str,
):

    value = raw.strip()

    if field_path == "population.age_min":

        try:
            return float(value)

        except ValueError as exc:
            raise ValueError(
                "最低年龄必须是数字。"
            ) from exc

    if field_path == "covariates":

        return [
            item.strip()
            for item in value.split(",")
            if item.strip()
        ]

    return (
        value
        if value
        else None
    )


def review_proposal(
    proposal,
):

    selections = {}

    print()
    print("========================================")
    print(" Research Planning V0.2 人工审核")
    print("========================================")

    for item in proposal.items:

        print()
        print("----------------------------------------")
        print(
            f"【{item.title}】"
        )
        print("----------------------------------------")
        print(
            f"字段：{item.field_path}"
        )
        print(
            f"来源：{item.provenance}"
        )
        print(
            f"说明：{item.reason}"
        )

        if (
            item.current_value
            not in (None, [])
        ):

            print(
                "当前值："
            )
            print(
                item.current_value
            )

            if ask_yes_no(
                "是否保留当前值？"
            ):
                continue

        if item.options:

            print()
            print(
                "可选项："
            )

            for index, option in enumerate(
                item.options,
                start=1,
            ):

                print(
                    f"{index}. "
                    f"{option.label} "
                    f"[{option.value}]"
                )

                if option.description:
                    print(
                        f"   {option.description}"
                    )

            if item.allow_custom:
                print(
                    f"{len(item.options) + 1}. 自定义输入"
                )

            while True:

                raw_choice = input(
                    "请选择："
                ).strip()

                try:
                    choice = int(
                        raw_choice
                    )

                except ValueError:
                    print(
                        "请输入合法编号。"
                    )
                    continue

                if (
                    1
                    <= choice
                    <= len(item.options)
                ):

                    selections[
                        item.field_path
                    ] = (
                        item.options[
                            choice - 1
                        ].value
                    )
                    break

                if (
                    item.allow_custom
                    and choice
                    == len(item.options) + 1
                ):

                    raw = input(
                        "请输入自定义内容："
                    )

                    selections[
                        item.field_path
                    ] = (
                        parse_custom_value(
                            item.field_path,
                            raw,
                        )
                    )
                    break

                print(
                    "无效选择。"
                )

            continue

        if item.allow_custom:

            raw = input(
                "请输入最终值"
                + (
                    "（多个协变量用英文逗号分隔）"
                    if item.field_path
                    == "covariates"
                    else ""
                )
                + "："
            )

            value = (
                parse_custom_value(
                    item.field_path,
                    raw,
                )
            )

            if (
                value in (None, [])
                and item.blocking
            ):
                raise RuntimeError(
                    f"{item.title} 为必填项。"
                )

            selections[
                item.field_path
            ] = value

            continue

        if item.blocking:
            raise RuntimeError(
                f"必填审核项没有可用选择："
                f"{item.field_path}"
            )

    return selections


print()
print("========================================")
print(" 医学数据分析工作流平台")
print(" Research Planning V0.2 Demo")
print("========================================")
print()

question = input(
    "请输入研究问题：\n> "
).strip()

if not question:
    raise RuntimeError(
        "研究问题不能为空。"
    )


print()
print(
    "正在调用 DeepSeek 进行语义提取……"
)

candidate = (
    ResearchSpecGenerator()
    .generate(
        question
    )
)


print()
print("========================================")
print("机器提取层：Candidate Research Spec")
print("========================================")
print_json(
    candidate
)


proposal = (
    ProposalBuilderV02
    .build(
        candidate
    )
)


print()
print("========================================")
print("审核层：Candidate Proposal")
print("========================================")
print(
    "Proposal ID："
    f"{proposal.proposal_id}"
)

selections = (
    review_proposal(
        proposal
    )
)


reviewed_candidate, review_log = (
    ReviewEngineV02
    .apply(
        proposal=proposal,
        selections=selections,
        reviewed_by="demo_user",
    )
)


execution_spec = (
    ExecutionSpecBuilderV02
    .build(
        reviewed_candidate=reviewed_candidate,
        review_log=review_log,
    )
)


print()
print("========================================")
print("最终执行方案预览")
print("========================================")
print_json(
    execution_spec
)


if not ask_yes_no(
    "是否正式冻结以上 Execution Research Spec？"
):

    print()
    print(
        "未冻结。本次审核结果不会作为正式执行方案。"
    )

    sys.exit(0)


frozen = (
    ExecutionSpecFreezeServiceV02
    .freeze(
        execution_spec=execution_spec,
        review_log=review_log,
    )
)


store = (
    ResearchPlanningStoreV02(
        project_root
        / "artifacts"
        / "planning_v02"
    )
)

saved_dir = (
    store.save_bundle(
        proposal=proposal,
        review_log=review_log,
        frozen_spec=frozen,
    )
)


print()
print("========================================")
print("V0.2 Research Spec 已正式冻结")
print("========================================")
print()
print(
    f"Spec ID：{frozen.spec_id}"
)
print(
    f"Version：V{frozen.spec_version}"
)
print(
    f"Review ID：{frozen.review_id}"
)
print(
    f"Reviewed By：{frozen.reviewed_by}"
)
print(
    f"Content Hash：{frozen.content_hash}"
)
print()
print(
    "已保存三个独立产物："
)
print(
    saved_dir
    / "proposal.json"
)
print(
    saved_dir
    / "review_log.json"
)
print(
    saved_dir
    / "execution_spec.json"
)
print()
print(
    "后续 Rule / YAML / Workflow "
    "只允许读取 execution_spec.json。"
)
