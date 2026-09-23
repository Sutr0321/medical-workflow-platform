from medflow.contracts.candidate_spec import (
    CandidateResearchSpecV01,
)
from medflow.conversation.readiness_v03 import (
    ConversationalReadinessV03,
)


class ResearchPlanPreviewV03:
    """
    人类可读的研究方案预览。

    后续 Web 前端可以直接把同一份结构化状态
    渲染成右侧“实时方案预览”面板。
    """

    LABELS = {
        "study_design": "研究设计",
        "objective": "研究目的",
        "dataset.name": "数据来源",
        "population.age_min": "最低年龄",
        "exposure.name": "主要暴露",
        "exposure.data_type": "暴露变量类型",
        "exposure.analysis_form": "暴露分析形式",
        "exposure.unit": "计划报告单位",
        "outcome.name": "主要结局",
        "outcome.data_type": "结局变量类型",
        "outcome.definition": "结局定义",
        "covariates": "协变量",
        "missing_data.strategy": "缺失值处理",
        "analysis.method": "主分析方法",
    }

    @staticmethod
    def render(
        spec: CandidateResearchSpecV01,
        confirmed_fields: list[str],
    ) -> str:

        data = spec.model_dump()

        rows = [
            (
                "study_design",
                data["study_design"],
            ),
            (
                "objective",
                data["objective"],
            ),
            (
                "dataset.name",
                data["dataset"]["name"],
            ),
            (
                "population.age_min",
                data["population"]["age_min"],
            ),
            (
                "exposure.name",
                data["exposure"]["name"],
            ),
            (
                "exposure.data_type",
                data["exposure"]["data_type"],
            ),
            (
                "exposure.analysis_form",
                data["exposure"]["analysis_form"],
            ),
            (
                "exposure.unit",
                data["exposure"]["unit"],
            ),
            (
                "outcome.name",
                data["outcome"]["name"],
            ),
            (
                "outcome.data_type",
                data["outcome"]["data_type"],
            ),
            (
                "outcome.definition",
                data["outcome"]["definition"],
            ),
            (
                "covariates",
                [
                    item["name"]
                    for item
                    in data["covariates"]
                ],
            ),
            (
                "missing_data.strategy",
                data["missing_data"]["strategy"],
            ),
            (
                "analysis.method",
                data["analysis"]["method"],
            ),
        ]

        missing = set(
            ConversationalReadinessV03
            .missing_fields(spec)
        )

        lines = [
            "========================================",
            "研究方案实时预览",
            "========================================",
        ]

        confirmed = set(
            confirmed_fields
        )

        for path, value in rows:

            label = (
                ResearchPlanPreviewV03
                .LABELS[path]
            )

            if path in missing:
                marker = "⚠"
                shown = "待讨论"

            elif path in confirmed:
                marker = "✅"
                shown = (
                    ResearchPlanPreviewV03
                    ._format_value(value)
                )

            elif value not in (
                None,
                [],
                "",
            ):
                marker = "◌"
                shown = (
                    ResearchPlanPreviewV03
                    ._format_value(value)
                    + "（已提取，建议最终预览时确认）"
                )

            else:
                marker = "—"
                shown = "未设置"

            lines.append(
                f"{marker} {label}：{shown}"
            )

        return "\n".join(lines)

    @staticmethod
    def _format_value(
        value,
    ) -> str:

        if isinstance(value, list):
            return (
                "、".join(
                    str(item)
                    for item in value
                )
                if value
                else "无"
            )

        return str(value)
