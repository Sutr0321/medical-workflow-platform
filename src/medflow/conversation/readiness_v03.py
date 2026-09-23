from medflow.contracts.candidate_spec import (
    CandidateResearchSpecV01,
)


class ConversationalReadinessV03:
    """
    对话规划阶段的确定性完整性检查。

    这里只判断 Research Plan 是否足够完整，
    不判断当前平台是否具备执行能力。
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
    def blocking_reasons(
        spec: CandidateResearchSpecV01,
    ) -> list[str]:
        """
        除字段缺失外，再检查方案内部逻辑冲突。
        """

        reasons = [
            f"必填研究决策尚未完成：{path}"
            for path in (
                ConversationalReadinessV03
                .missing_fields(spec)
            )
        ]

        method = (
            spec.analysis.method or ""
        ).lower()

        if (
            "multivariable" in method
            or "multivariate" in method
            or "多变量" in method
            or "多因素" in method
        ):
            if not spec.covariates:
                reasons.append(
                    "主分析已设为多变量/多因素模型，"
                    "但协变量框架仍为空。"
                )

        return reasons

    @staticmethod
    def discussion_targets(
        spec: CandidateResearchSpecV01,
        confirmed_fields: list[str],
    ) -> list[str]:

        confirmed = set(
            confirmed_fields
        )

        targets = [
            path
            for path in (
                ConversationalReadinessV03
                .missing_fields(spec)
            )
            if path not in confirmed
        ]

        method = (
            spec.analysis.method or ""
        ).lower()

        needs_covariates = (
            (
                "multivariable" in method
                or "multivariate" in method
                or "多变量" in method
                or "多因素" in method
            )
            and not spec.covariates
        )

        if (
            needs_covariates
            and "covariates"
            not in confirmed
            and "covariates"
            not in targets
        ):
            targets.insert(
                0,
                "covariates",
            )

        return targets

    @staticmethod
    def is_ready(
        spec: CandidateResearchSpecV01,
    ) -> bool:

        return not (
            ConversationalReadinessV03
            .blocking_reasons(spec)
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
