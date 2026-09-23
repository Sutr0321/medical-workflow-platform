from medflow.contracts.candidate_spec import (
    CandidateResearchSpecV01,
)


class ConversationalReadinessV03:
    """
    V0.3 对话规划阶段的确定性完整性检查。

    这里不调用 LLM。
    它只回答：
    “当前 Research Plan 还缺哪些正式冻结所需字段？”
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
