from medflow.contracts.candidate_spec import (
    CandidateResearchSpecV01,
)
from medflow.conversation.readiness_v03 import (
    ConversationalReadinessV03,
)


class ResearchPlanPreviewV03:
    """
    人类可读的 Rich Research Plan 预览。
    """

    @staticmethod
    def render(
        spec: CandidateResearchSpecV01,
        confirmed_fields: list[str],
    ) -> str:

        data = spec.model_dump()

        lines = [
            "========================================",
            "研究方案实时预览",
            "========================================",
        ]

        confirmed = set(
            confirmed_fields
        )

        missing = set(
            ConversationalReadinessV03
            .missing_fields(spec)
        )

        def add_row(
            path: str,
            label: str,
            value,
            *,
            optional: bool = False,
        ):

            if path in missing:
                marker = "⚠"
                shown = "待讨论"

            elif value in (
                None,
                "",
                [],
            ):
                marker = "—"
                shown = (
                    "未设置"
                    if optional
                    else "待讨论"
                )

            elif path in confirmed:
                marker = "✅"
                shown = (
                    ResearchPlanPreviewV03
                    ._format_value(value)
                )

            else:
                marker = "◌"
                shown = (
                    ResearchPlanPreviewV03
                    ._format_value(value)
                    + "（已提取，建议最终预览时确认）"
                )

            lines.append(
                f"{marker} {label}：{shown}"
            )

        add_row(
            "study_design",
            "研究设计",
            data["study_design"],
        )

        add_row(
            "objective",
            "研究目的",
            data["objective"],
        )

        add_row(
            "dataset.name",
            "数据来源",
            data["dataset"]["name"],
        )

        add_row(
            "dataset.version",
            "数据周期/版本",
            data["dataset"]["version"],
            optional=True,
        )

        add_row(
            "population.age_min",
            "最低年龄",
            data["population"]["age_min"],
        )

        add_row(
            "exposure.name",
            "主要暴露",
            data["exposure"]["name"],
        )

        add_row(
            "exposure.data_type",
            "暴露变量类型",
            data["exposure"]["data_type"],
        )

        add_row(
            "exposure.analysis_form",
            "暴露分析形式",
            data["exposure"]["analysis_form"],
        )

        add_row(
            "exposure.unit",
            "计划报告单位",
            data["exposure"]["unit"],
            optional=True,
        )

        add_row(
            "outcome.name",
            "主要结局",
            data["outcome"]["name"],
        )

        add_row(
            "outcome.data_type",
            "结局变量类型",
            data["outcome"]["data_type"],
        )

        add_row(
            "outcome.definition",
            "主结局定义",
            data["outcome"]["definition"],
        )

        add_row(
            "outcome.sensitivity_definitions",
            "结局敏感性定义",
            data["outcome"][
                "sensitivity_definitions"
            ],
            optional=True,
        )

        add_row(
            "covariates",
            "协变量",
            [
                item["name"]
                for item in data["covariates"]
            ],
        )

        add_row(
            "missing_data.strategy",
            "缺失值总策略",
            data["missing_data"]["strategy"],
        )

        add_row(
            "missing_data.mode",
            "缺失值策略模式",
            data["missing_data"]["mode"],
            optional=True,
        )

        add_row(
            "missing_data.assessment",
            "缺失值评估内容",
            data["missing_data"]["assessment"],
            optional=True,
        )

        add_row(
            "missing_data.decision_rule",
            "缺失值决策规则",
            data["missing_data"]["decision_rule"],
            optional=True,
        )

        add_row(
            "missing_data.sensitivity_plan",
            "缺失值敏感性分析",
            data["missing_data"]["sensitivity_plan"],
            optional=True,
        )

        add_row(
            "analysis.method",
            "主分析方法",
            data["analysis"]["method"],
        )

        add_row(
            "analysis.effect_measure",
            "主要效应量",
            data["analysis"]["effect_measure"],
            optional=True,
        )

        ci_level = (
            data["analysis"]["ci_level"]
        )

        ci_display = (
            f"{int(ci_level * 100)}%"
            if isinstance(
                ci_level,
                (int, float),
            )
            else ci_level
        )

        add_row(
            "analysis.ci_level",
            "置信区间",
            ci_display,
            optional=True,
        )

        add_row(
            "analysis.survey_design_required",
            "复杂抽样设计",
            (
                "需要"
                if data["analysis"][
                    "survey_design_required"
                ] is True
                else (
                    "不需要"
                    if data["analysis"][
                        "survey_design_required"
                    ] is False
                    else None
                )
            ),
            optional=True,
        )

        add_row(
            "analysis.secondary_analyses",
            "次要分析",
            data["analysis"][
                "secondary_analyses"
            ],
            optional=True,
        )

        add_row(
            "analysis.sensitivity_analyses",
            "分析敏感性方案",
            data["analysis"][
                "sensitivity_analyses"
            ],
            optional=True,
        )

        blockers = (
            ConversationalReadinessV03
            .blocking_reasons(spec)
        )

        lines.append("")
        lines.append(
            "冻结检查："
            + (
                "可冻结"
                if not blockers
                else "不可冻结"
            )
        )

        for reason in blockers:
            lines.append(
                f"⚠ {reason}"
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

        if isinstance(value, float):
            if value.is_integer():
                return str(
                    int(value)
                )

        return str(value)
