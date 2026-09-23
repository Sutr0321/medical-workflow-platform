from medflow.contracts.candidate_spec import (
    CandidateResearchSpecV01,
)


class ConversationalReadinessV03:
    """
    对话规划阶段的确定性完整性检查。

    只回答“研究计划还缺什么”，
    不判断当前平台能不能执行。
    """

    REQUIRED_PATHS = (
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
        "missing_data.strategy",
        "analysis.method",
    )

    @staticmethod
    def missing_fields(
        spec: CandidateResearchSpecV01,
    ) -> list[str]:

        data = spec.model_dump()

        missing: list[str] = []

        for path in (
            ConversationalReadinessV03
            .REQUIRED_PATHS
        ):

            value = (
                ConversationalReadinessV03
                ._get_value(
                    data,
                    path,
                )
            )

            if value is None:
                missing.append(path)
                continue

            if (
                isinstance(value, str)
                and not value.strip()
            ):
                missing.append(path)

        return missing

    @staticmethod
    def discussion_targets(
        spec: CandidateResearchSpecV01,
        confirmed_fields: list[str],
    ) -> list[str]:
        """
        返回下一轮允许 AI 主动追问的字段。

        核心规则：
        已确认字段不再主动询问。
        用户如果主动提出修改，仍然允许更新。
        """

        confirmed = set(
            confirmed_fields
        )

        return [
            path
            for path in (
                ConversationalReadinessV03
                .missing_fields(spec)
            )
            if path not in confirmed
        ]

    @staticmethod
    def is_ready(
        spec: CandidateResearchSpecV01,
    ) -> bool:

        return not (
            ConversationalReadinessV03
            .missing_fields(spec)
        )

    @staticmethod
    def _get_value(
        data: dict,
        path: str,
    ):

        current = data

        for token in path.split("."):

            if not isinstance(
                current,
                dict,
            ):
                return None

            current = current.get(
                token
            )

        return current
