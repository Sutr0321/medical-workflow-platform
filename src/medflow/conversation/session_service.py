import uuid
from datetime import datetime, timezone
from typing import Any

from medflow.contracts.candidate_spec import (
    CandidateResearchSpecV01,
)
from medflow.contracts.planning_session import (
    PlanningDecisionV03,
    PlanningMessageV03,
    PlanningSessionV03,
)
from medflow.conversation.agent import (
    ConversationalPlanningAgentV03,
)
from medflow.conversation.readiness_v03 import (
    ConversationalReadinessV03,
)
from medflow.llm.spec_generator import (
    ResearchSpecGenerator,
)
from medflow.spec.candidate_updater import (
    CandidateSpecUpdater,
)


class PlanningSessionServiceV03:
    """
    对话式 Research Planning 会话服务。

    用户看到的是聊天；
    后台持续维护 Candidate Research Spec。
    """

    def __init__(self):
        self.initial_extractor = (
            ResearchSpecGenerator()
        )
        self.agent = (
            ConversationalPlanningAgentV03()
        )

    def start(
        self,
        topic: str,
    ) -> PlanningSessionV03:

        topic = topic.strip()

        if not topic:
            raise ValueError(
                "课题主题不能为空。"
            )

        candidate = (
            self.initial_extractor
            .generate(topic)
        )

        now = datetime.now(
            timezone.utc
        )

        explicit_paths = (
            self._collect_explicit_paths(
                candidate
            )
        )

        decisions = [
            PlanningDecisionV03(
                field_path=path,
                value=self._get_path_value(
                    candidate.model_dump(),
                    path,
                ),
                evidence=topic,
                decided_at=now,
            )
            for path in explicit_paths
        ]

        session = PlanningSessionV03(
            session_id=(
                "PS-"
                + uuid.uuid4().hex[
                    :12
                ].upper()
            ),
            status="DISCUSSING",
            messages=[
                PlanningMessageV03(
                    role="user",
                    content=topic,
                    created_at=now,
                )
            ],
            current_candidate=candidate,
            confirmed_fields=explicit_paths,
            decisions=decisions,
            pending_suggestions=[],
            created_at=now,
            updated_at=now,
        )

        return self.continue_dialogue(
            session=session,
            user_message=None,
        )

    def continue_dialogue(
        self,
        *,
        session: PlanningSessionV03,
        user_message: str | None,
    ) -> PlanningSessionV03:

        if session.status == "FROZEN":
            raise ValueError(
                "当前 Planning Session 已冻结，"
                "不能继续修改。"
            )

        data = session.model_dump()

        now = datetime.now(
            timezone.utc
        )

        if user_message is not None:

            user_message = (
                user_message.strip()
            )

            if not user_message:
                raise ValueError(
                    "用户消息不能为空。"
                )

            data["messages"].append(
                PlanningMessageV03(
                    role="user",
                    content=user_message,
                    created_at=now,
                ).model_dump()
            )

        latest_user_message = (
            user_message
            if user_message is not None
            else session.messages[-1].content
        )

        history = [
            {
                "role": item["role"],
                "content": item["content"],
            }
            for item in data["messages"]
        ]

        candidate = (
            CandidateResearchSpecV01
            .model_validate(
                data[
                    "current_candidate"
                ]
            )
        )

        missing = (
            ConversationalReadinessV03
            .missing_fields(candidate)
        )

        turn = self.agent.respond(
            user_message=latest_user_message,
            conversation_history=history,
            current_state=(
                candidate.model_dump(
                    mode="json"
                )
            ),
            missing_fields=missing,
            pending_suggestions=(
                data[
                    "pending_suggestions"
                ]
            ),
        )

        answers: dict[str, Any] = {}

        confirmed_fields = list(
            data[
                "confirmed_fields"
            ]
        )

        decisions = list(
            data[
                "decisions"
            ]
        )

        for update in (
            turn.explicit_updates
        ):

            normalized = (
                self._normalize_value(
                    update.field_path,
                    update.value,
                )
            )

            answers[
                update.field_path
            ] = normalized

            if (
                update.field_path
                not in confirmed_fields
            ):
                confirmed_fields.append(
                    update.field_path
                )

            decisions.append(
                PlanningDecisionV03(
                    field_path=(
                        update.field_path
                    ),
                    value=(
                        update.value
                    ),
                    evidence=(
                        update.evidence
                    ),
                    decided_at=now,
                ).model_dump()
            )

        if answers:

            candidate = (
                CandidateSpecUpdater
                .apply_answers(
                    spec=candidate,
                    answers=answers,
                )
            )

        data[
            "current_candidate"
        ] = candidate.model_dump()

        data[
            "confirmed_fields"
        ] = confirmed_fields

        data[
            "decisions"
        ] = decisions

        data[
            "pending_suggestions"
        ] = [
            item.model_dump()
            for item in turn.suggestions
        ]

        data["messages"].append(
            PlanningMessageV03(
                role="assistant",
                content=(
                    turn.assistant_message
                ),
                created_at=now,
            ).model_dump()
        )

        data["updated_at"] = now

        data["status"] = (
            "READY_TO_FREEZE"
            if (
                ConversationalReadinessV03
                .is_ready(candidate)
            )
            else "DISCUSSING"
        )

        return (
            PlanningSessionV03
            .model_validate(data)
        )

    @staticmethod
    def _normalize_value(
        field_path: str,
        value,
    ):

        if field_path == "covariates":

            if value is None:
                return []

            if not isinstance(
                value,
                list,
            ):
                raise ValueError(
                    "协变量必须是列表。"
                )

            return [
                {
                    "name": str(item).strip(),
                    "column": None,
                    "data_type": None,
                    "unit": None,
                    "reference_value": None,
                }
                for item in value
                if str(item).strip()
            ]

        return value

    @staticmethod
    def _collect_explicit_paths(
        spec: CandidateResearchSpecV01,
    ) -> list[str]:

        data = spec.model_dump()

        candidate_paths = (
            "study_design",
            "objective",
            "dataset.name",
            "dataset.version",
            "population.description",
            "population.age_min",
            "population.age_max",
            "exposure.name",
            "exposure.data_type",
            "exposure.unit",
            "exposure.analysis_form",
            "outcome.name",
            "outcome.data_type",
            "outcome.definition",
            "missing_data.strategy",
            "analysis.method",
        )

        result: list[str] = []

        for path in candidate_paths:

            current = (
                PlanningSessionServiceV03
                ._get_path_value(
                    data,
                    path,
                )
            )

            if current not in (
                None,
                "",
            ):
                result.append(path)

        if data["covariates"]:
            result.append(
                "covariates"
            )

        return result

    @staticmethod
    def _get_path_value(
        data: dict,
        path: str,
    ):

        if path == "covariates":
            return [
                item["name"]
                for item in data["covariates"]
            ]

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
