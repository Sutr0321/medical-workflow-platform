import re
import uuid
from datetime import datetime, timezone
from typing import Any

from medflow.contracts.candidate_spec import (
    CandidateResearchSpecV01,
)
from medflow.contracts.planning_session import (
    PlanningAgentTurnV03,
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

    核心顺序：

    用户消息
    → 先解释并落结构化状态
    → 重新计算未解决字段
    → 再生成 AI 回复

    因此 AI 的下一句话看到的一定是“更新后的状态”。
    """

    MAX_ACTIVE_TARGETS = 2

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

        return self._compose_after_state_update(
            session=session,
            latest_user_message=topic,
        )

    def continue_dialogue(
        self,
        *,
        session: PlanningSessionV03,
        user_message: str,
    ) -> PlanningSessionV03:

        if session.status == "FROZEN":
            raise ValueError(
                "当前 Planning Session 已冻结，"
                "不能继续修改。"
            )

        user_message = user_message.strip()

        if not user_message:
            raise ValueError(
                "用户消息不能为空。"
            )

        now = datetime.now(
            timezone.utc
        )

        data = session.model_dump()

        data["messages"].append(
            PlanningMessageV03(
                role="user",
                content=user_message,
                created_at=now,
            ).model_dump()
        )

        candidate = (
            CandidateResearchSpecV01
            .model_validate(
                data[
                    "current_candidate"
                ]
            )
        )

        history = [
            {
                "role": item["role"],
                "content": item["content"],
            }
            for item in data["messages"]
        ]

        # ----------------------------------
        # Phase 1：只理解用户本轮明确决策
        # ----------------------------------

        updates = (
            self.agent
            .safe_interpret_updates(
                user_message=user_message,
                conversation_history=history,
                current_state=(
                    candidate.model_dump(
                        mode="json"
                    )
                ),
                pending_suggestions=(
                    data[
                        "pending_suggestions"
                    ]
                ),
            )
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

        for update in updates:

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

        (
            candidate,
            normalization_decisions,
        ) = (
            self._normalize_resolved_dependencies(
                candidate=candidate,
                answers=answers,
                decided_at=now,
            )
        )

        decisions.extend(
            item.model_dump()
            for item in normalization_decisions
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

        data["updated_at"] = now

        updated_session = (
            PlanningSessionV03
            .model_validate(data)
        )

        # ----------------------------------
        # Phase 2：用更新后的状态生成下一句话
        # ----------------------------------

        return self._compose_after_state_update(
            session=updated_session,
            latest_user_message=user_message,
        )

    def _compose_after_state_update(
        self,
        *,
        session: PlanningSessionV03,
        latest_user_message: str,
    ) -> PlanningSessionV03:

        data = session.model_dump()

        candidate = (
            CandidateResearchSpecV01
            .model_validate(
                data[
                    "current_candidate"
                ]
            )
        )

        targets = (
            ConversationalReadinessV03
            .discussion_targets(
                candidate,
                data[
                    "confirmed_fields"
                ],
            )
        )

        # 每轮最多推进两个真正未解决的问题。
        active_targets = (
            targets[
                :self.MAX_ACTIVE_TARGETS
            ]
        )

        history = [
            {
                "role": item["role"],
                "content": item["content"],
            }
            for item in data["messages"]
        ]

        deterministic_turn = (
            self._deterministic_turn_if_applicable(
                session_status=(
                    session.status
                ),
                active_targets=(
                    active_targets
                ),
            )
        )

        if deterministic_turn is not None:
            turn = deterministic_turn

        else:
            turn = (
                self.agent
                .safe_compose_reply(
                    latest_user_message=(
                        latest_user_message
                    ),
                    conversation_history=history,
                    current_state=(
                        candidate.model_dump(
                            mode="json"
                        )
                    ),
                    confirmed_fields=(
                        data[
                            "confirmed_fields"
                        ]
                    ),
                    discussion_targets=(
                        active_targets
                    ),
                )
            )

        now = datetime.now(
            timezone.utc
        )

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
    def _normalize_resolved_dependencies(
        *,
        candidate: CandidateResearchSpecV01,
        answers: dict[str, Any],
        decided_at: datetime,
    ) -> tuple[
        CandidateResearchSpecV01,
        list[PlanningDecisionV03],
    ]:
        """
        当某个上游研究决策已经明确后，
        清理同一份 Candidate 中已经失效的“等待该决策”措辞。

        这里只做不改变研究意图的确定性文本规范化，
        并记录 SYSTEM_NORMALIZATION 审计事件。
        """

        if (
            "dataset.version"
            not in answers
            or not answers[
                "dataset.version"
            ]
        ):
            return candidate, []

        definition = (
            candidate.outcome.definition
            or ""
        )

        if not definition:
            return candidate, []

        normalized = re.sub(
            (
                r"[，,]?(?:等|待)确定\s*NHANES\s*调查周期后"
                r"[，,]?在数据绑定阶段"
                r"(?:按照|依据|根据)官方文档核对"
            ),
            (
                "，后续在数据绑定阶段依据已确定的 "
                "NHANES 调查周期和官方文档核对"
            ),
            definition,
        )

        if normalized == definition:
            return candidate, []

        updated = (
            CandidateSpecUpdater
            .apply_answers(
                spec=candidate,
                answers={
                    "outcome.definition": normalized,
                },
            )
        )

        decision = PlanningDecisionV03(
            field_path="outcome.definition",
            value=normalized,
            evidence=(
                "dataset.version 已明确；"
                "系统仅清理原定义中已失效的"
                "“待确定 NHANES 调查周期后”措辞，"
                "不改变结局定义本身。"
            ),
            source="SYSTEM_NORMALIZATION",
            decided_at=decided_at,
        )

        return updated, [
            decision
        ]


    @staticmethod
    def _deterministic_turn_if_applicable(
        *,
        session_status: str,
        active_targets: list[str],
    ) -> PlanningAgentTurnV03 | None:
        """
        对少数“系统状态已足够明确”的场景使用确定性回复，
        避免 LLM 为了丰富措辞而补充未经核验的数据库事实。

        1. 只剩 NHANES 调查周期未定：
           只问周期，不给未经 Evidence 核对的具体周期推荐。

        2. 从 DISCUSSING 刚进入完整状态：
           只告诉用户方案已具备预览/冻结条件，
           不再让 LLM 额外总结并引入新事实。
        """

        if active_targets == [
            "dataset.version"
        ]:
            return PlanningAgentTurnV03(
                assistant_message=(
                    "当前核心研究设计已经基本明确，"
                    "冻结前还需要确定计划使用的 NHANES 调查周期。"
                    "调查周期属于研究范围本身，会影响研究时间范围、"
                    "样本量以及后续变量可用性和可比性评估。"
                    "请直接告诉我希望使用哪个或哪些周期。"
                    "具体文件、变量名、权重、PSU、strata 和派生规则，"
                    "后续在 Data Binding 阶段依据官方资料核对。"
                ),
                explicit_updates=[],
                suggestions=[],
            )

        if (
            not active_targets
            and session_status
            == "DISCUSSING"
        ):
            return PlanningAgentTurnV03(
                assistant_message=(
                    "已记录你刚才明确的研究决策。"
                    "当前 Research Plan 的核心字段已经完整，"
                    "可以输入“预览方案”检查结构化内容，"
                    "也可以继续主动修改；确认无误后再输入“冻结方案”，"
                    "由系统执行正式冻结。"
                ),
                explicit_updates=[],
                suggestions=[],
            )

        return None


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

        if field_path in {
            "outcome.sensitivity_definitions",
            "missing_data.assessment",
            "analysis.secondary_analyses",
            "analysis.sensitivity_analyses",
        }:

            if value is None:
                return []

            if not isinstance(
                value,
                list,
            ):
                raise ValueError(
                    f"{field_path} 必须是列表。"
                )

            return [
                str(item).strip()
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
            "outcome.sensitivity_definitions",
            "missing_data.strategy",
            "missing_data.mode",
            "missing_data.assessment",
            "missing_data.decision_rule",
            "missing_data.sensitivity_plan",
            "analysis.method",
            "analysis.effect_measure",
            "analysis.ci_level",
            "analysis.survey_design_required",
            "analysis.secondary_analyses",
            "analysis.sensitivity_analyses",
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
                [],
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
