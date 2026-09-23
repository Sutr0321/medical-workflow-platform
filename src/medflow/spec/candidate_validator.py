from medflow.contracts.candidate_spec import (
    CandidateResearchSpecV01,
    OpenIssue,
)


class CandidateSpecValidator:
    """
    Research Spec 的固定规则校验器。

    注意：
    这里不调用 LLM。

    同一个 Candidate Research Spec
    必须永远得到相同的 open_issues。
    """

    @staticmethod
    def validate(
        spec: CandidateResearchSpecV01,
    ) -> list[OpenIssue]:

        issues: list[OpenIssue] = []

        def add_issue(
            field_path: str,
            issue_type: str,
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
                    issue_type=issue_type,
                    blocking=blocking,
                    question=question,
                )
            )

        # ======================================
        # 研究设计
        # ======================================

        if spec.study_design is None:

            add_issue(
                field_path="study_design",
                issue_type="missing",
                blocking=True,
                question=(
                    "请确认本研究是否为横断面研究。"
                ),
            )

        # ======================================
        # 数据集
        # ======================================

        if spec.dataset.name is None:

            add_issue(
                field_path="dataset.name",
                issue_type="missing",
                blocking=False,
                question=(
                    "请说明计划使用的数据来源或数据集；"
                    "如暂未确定可稍后补充。"
                ),
            )

        # ======================================
        # 研究人群
        # ======================================

        if spec.population.age_min is None:

            add_issue(
                field_path="population.age_min",
                issue_type="missing",
                blocking=True,
                question=(
                    "请明确研究对象的最低年龄。"
                ),
            )

        # ======================================
        # 暴露变量
        # ======================================

        if spec.exposure.data_type is None:

            add_issue(
                field_path="exposure.data_type",
                issue_type="missing",
                blocking=True,
                question=(
                    "请确认暴露变量是连续变量、"
                    "分类变量还是二分类变量。"
                ),
            )

        if spec.exposure.analysis_form is None:

            add_issue(
                field_path="exposure.analysis_form",
                issue_type="missing",
                blocking=True,
                question=(
                    "请确认暴露变量以连续形式"
                    "还是分类形式进入分析。"
                ),
            )

        if spec.exposure.unit is None:

            add_issue(
                field_path="exposure.unit",
                issue_type="missing",
                blocking=False,
                question=(
                    "如适用，请确认暴露变量的单位。"
                ),
            )

        # ======================================
        # 结局变量
        # ======================================

        if spec.outcome.data_type is None:

            add_issue(
                field_path="outcome.data_type",
                issue_type="missing",
                blocking=True,
                question=(
                    "请确认结局是否为二分类变量。"
                ),
            )

        if spec.outcome.definition is None:

            add_issue(
                field_path="outcome.definition",
                issue_type="missing",
                blocking=True,
                question=(
                    "请明确结局变量的定义或判定标准。"
                ),
            )

        # ======================================
        # 分析方法
        # ======================================

        if spec.analysis.method is None:

            add_issue(
                field_path="analysis.method",
                issue_type="missing",
                blocking=True,
                question=(
                    "请确认本研究的主分析方法。"
                    "当前 V0.1 支持 Logistic 回归。"
                ),
            )

        # ======================================
        # 缺失值处理
        # ======================================

        if spec.missing_data.strategy is None:

            add_issue(
                field_path="missing_data.strategy",
                issue_type="missing",
                blocking=True,
                question=(
                    "请确认本研究的缺失值处理策略。"
                ),
            )

        return issues