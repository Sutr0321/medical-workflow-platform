from pydantic import BaseModel, Field

from medflow.contracts.research_plan import (
    ResearchPlanV03,
)


class ExecutionCapabilityReportV03(BaseModel):
    """
    当前平台执行能力检查结果。

    这个结果不能反向修改 Research Plan。
    """
    supported: bool

    unsupported_reasons: list[str] = Field(
        default_factory=list
    )


class ExecutionCapabilityCheckerV03:
    """
    把“科研方案是什么”和“平台现在能不能跑”彻底分开。

    当前最小执行闭环仍只实现：
    - cross_sectional
    - association
    - binary outcome
    - logistic_regression
    - complete_case_global

    但 Research Plan 可以合法冻结其他科研选择。
    """

    @staticmethod
    def check(
        plan: ResearchPlanV03,
    ) -> ExecutionCapabilityReportV03:

        reasons: list[str] = []

        if (
            plan.study_design
            != "cross_sectional"
        ):
            reasons.append(
                "当前执行引擎尚未实现该研究设计："
                f"{plan.study_design}"
            )

        if (
            plan.objective
            != "association"
        ):
            reasons.append(
                "当前执行引擎尚未实现该研究目的："
                f"{plan.objective}"
            )

        if (
            plan.outcome.data_type
            != "binary"
        ):
            reasons.append(
                "当前执行引擎尚未实现该结局类型："
                f"{plan.outcome.data_type}"
            )

        if (
            plan.analysis.primary_model
            != "logistic_regression"
        ):
            reasons.append(
                "当前执行引擎尚未实现该主分析方法："
                f"{plan.analysis.primary_model}"
            )

        if (
            plan.analysis.survey_design_required
            is True
        ):
            reasons.append(
                "当前执行引擎尚未实现复杂抽样设计执行。"
            )

        if (
            plan.analysis.secondary_analyses
        ):
            reasons.append(
                "当前执行引擎尚未实现次要分析："
                + ", ".join(
                    plan.analysis.secondary_analyses
                )
            )

        if (
            plan.analysis.sensitivity_analyses
        ):
            reasons.append(
                "当前执行引擎尚未实现敏感性分析："
                + ", ".join(
                    plan.analysis.sensitivity_analyses
                )
            )

        if (
            plan.missing_data.strategy
            != "complete_case_global"
        ):
            reasons.append(
                "当前执行引擎尚未实现该缺失值策略："
                f"{plan.missing_data.strategy}"
            )

        return ExecutionCapabilityReportV03(
            supported=not reasons,
            unsupported_reasons=reasons,
        )
