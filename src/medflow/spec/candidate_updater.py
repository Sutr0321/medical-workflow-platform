import re
from typing import Any

from medflow.contracts.candidate_spec import (
    CandidateResearchSpecV01,
)
from medflow.spec.candidate_validator import (
    CandidateSpecValidator,
)


class CandidateSpecUpdater:
    """
    根据 field_path 更新 Candidate Research Spec。

    用户已经明确回答的问题，不再交给 AI 判断。

    更新后重新运行固定 Validator，
    已解决的问题会自动从 open_issues 中消失。
    """

    @staticmethod
    def apply_answers(
        spec: CandidateResearchSpecV01,
        answers: dict[str, Any],
    ) -> CandidateResearchSpecV01:

        # 转成普通 dict，避免直接修改原始 Pydantic 对象
        data = spec.model_dump()

        for field_path, value in answers.items():
            CandidateSpecUpdater._set_value(
                data=data,
                field_path=field_path,
                value=value,
            )

        # 重新经过 Pydantic Schema 校验
        updated_spec = CandidateResearchSpecV01.model_validate(
            data
        )

        # 重新由固定 Validator 生成问题
        updated_spec.open_issues = (
            CandidateSpecValidator.validate(
                updated_spec
            )
        )

        return updated_spec

    @staticmethod
    def _set_value(
        data: dict,
        field_path: str,
        value: Any,
    ) -> None:
        """
        支持：

        study_design
        population.age_min
        exposure.data_type
        outcome.definition

        以及未来：

        covariates[0].data_type
        """

        tokens = CandidateSpecUpdater._parse_path(
            field_path
        )

        current = data

        for token in tokens[:-1]:

            if isinstance(token, int):

                if not isinstance(current, list):
                    raise ValueError(
                        f"字段路径无效：{field_path}"
                    )

                if token >= len(current):
                    raise ValueError(
                        f"列表索引越界：{field_path}"
                    )

                current = current[token]

            else:

                if not isinstance(current, dict):
                    raise ValueError(
                        f"字段路径无效：{field_path}"
                    )

                if token not in current:
                    raise ValueError(
                        f"不存在的字段：{field_path}"
                    )

                current = current[token]

        last_token = tokens[-1]

        if isinstance(last_token, int):

            if not isinstance(current, list):
                raise ValueError(
                    f"字段路径无效：{field_path}"
                )

            current[last_token] = value

        else:

            if not isinstance(current, dict):
                raise ValueError(
                    f"字段路径无效：{field_path}"
                )

            if last_token not in current:
                raise ValueError(
                    f"不存在的字段：{field_path}"
                )

            current[last_token] = value

    @staticmethod
    def _parse_path(
        field_path: str,
    ) -> list[str | int]:

        tokens: list[str | int] = []

        parts = field_path.split(".")

        pattern = re.compile(
            r"([^\[\]]+)|\[(\d+)\]"
        )

        for part in parts:

            matches = pattern.findall(part)

            if not matches:
                raise ValueError(
                    f"无法解析字段路径：{field_path}"
                )

            for name, index in matches:

                if name:
                    tokens.append(name)

                elif index:
                    tokens.append(int(index))

        return tokens