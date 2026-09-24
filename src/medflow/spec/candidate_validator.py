from medflow.contracts.candidate_spec import (
    CandidateResearchSpecV01,
    OpenIssue,
)


class CandidateSpecValidator:
    """
    Research Planning 的固定规则校验器。

    这里不调用 LLM，也不判断当前平台是否已经实现某个算法。

    它只判断：
    “要形成一份可冻结的研究计划，还缺哪些科研决策？”
    """

    @staticmethod
    def validate(
        spec: CandidateResearchSpecV01,
    ) -> list[OpenIssue]:

        issues: list[OpenIssue] = []

        def add_issue(
            field_path: str,
            blocking: bool,
            question: str,
        ) -> None:

            issue_id = (
                f"ISSUE_{len(issues) + 1:03d}"
            )

            issues.append(
                OpenIssue(
                    issue_id=issue_id,
                    field_path=field_path,
                    issue_type="missing",
                    blocking=blocking,
                    question=question,
                )
            )

        if spec.study_design is None:
            add_issue(
                "study_design",
                True,
                "请明确研究设计。",
            )

        if spec.dataset.name is None:
            add_issue(
                "dataset.name",
                False,
                "请说明计划使用的数据来源或数据集；如暂未确定可稍后补充。",
            )

        elif (
            spec.dataset.name.strip().upper()
            == "NHANES"
            and (
                spec.dataset.version is None
                or not spec.dataset.version.strip()
            )
        ):
            add_issue(
                "dataset.version",
                True,
                "请明确计划使用的 NHANES 调查周期。"
                "调查周期属于研究范围，冻结前需要确定；"
                "具体文件、变量名、权重、PSU 和 strata "
                "仍留到 Data Binding 阶段核对。",
            )

        if spec.population.age_min is None:
            add_issue(
                "population.age_min",
                True,
                "请明确研究对象的最低年龄。",
            )

        if spec.exposure.data_type is None:
            add_issue(
                "exposure.data_type",
                True,
                "请明确暴露变量的数据类型。",
            )

        if spec.exposure.analysis_form is None:
            add_issue(
                "exposure.analysis_form",
                True,
                "请明确暴露变量进入主分析的形式。",
            )

        if spec.exposure.unit is None:
            add_issue(
                "exposure.unit",
                False,
                "如研究方案需要，请明确计划报告单位；真实源单位将在 Data Binding 阶段核对。",
            )

        if spec.outcome.data_type is None:
            add_issue(
                "outcome.data_type",
                True,
                "请明确结局变量的数据类型。",
            )

        if spec.outcome.definition is None:
            add_issue(
                "outcome.definition",
                True,
                "请明确结局变量的研究定义或判定标准。",
            )

        if spec.analysis.method is None:
            add_issue(
                "analysis.method",
                True,
                "请明确主分析方法。",
            )

        if spec.missing_data.strategy is None:
            add_issue(
                "missing_data.strategy",
                True,
                "请明确缺失值处理策略。",
            )

        return issues
