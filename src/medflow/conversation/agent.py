import json
import re

from medflow.contracts.planning_session import (
    PlanningAgentTurnV03,
    PlanningStateUpdateV03,
)
from medflow.llm.client import (
    create_deepseek_client,
)


class ConversationalPlanningAgentV03:
    """
    V0.3 对话式科研规划 Agent。

    每轮拆成两个阶段：

    1. interpret_updates
       只理解“用户刚刚明确了什么”，不负责追问。

    2. compose_reply
       在状态已经更新后，根据新的 unresolved targets
       生成自然语言回复和候选建议。

    这样可以从结构上避免：
    用户刚确认一个字段，AI 下一句话又重复询问它。
    """

    ALLOWED_UPDATE_PATHS = {
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
        "covariates",
        "missing_data.strategy",
        "analysis.method",
    }

    def __init__(
        self,
        client=None,
        max_attempts: int = 3,
    ):
        self.client = (
            client
            if client is not None
            else create_deepseek_client()
        )

        self.max_attempts = max(
            1,
            max_attempts,
        )

    def interpret_updates(
        self,
        *,
        user_message: str,
        conversation_history: list[dict],
        current_state: dict,
        pending_suggestions: list[dict],
    ) -> list[PlanningStateUpdateV03]:
        """
        第一阶段：只抽取用户本轮明确决定。

        不生成面向用户的回答，
        不提出新问题。
        """

        system_prompt = """
你是医学科研方案对话的“状态解释器”。

你的唯一任务：
根据当前用户消息、最近对话和上一轮候选建议，
判断用户这一轮明确确认、修改或接受了哪些研究决策。

严格规则：

1. 只记录用户明确表达的内容。
2. AI 自己之前提出但用户没有明确接受的建议，不能写入更新。
3. 用户可以用“1”“第3种”“就这个”“按你说的”等简短表达，
   需要结合最近对话和 pending_suggestions 理解。
4. 如果用户只是问问题、比较方案、要求解释，不产生更新。
5. 不因为医学常识自行补值。
6. 不因为“成年人”自动设 age_min=18。
7. 不自行确定疾病阈值。
8. 不自行选择统计方法或缺失值策略。
9. covariates 必须输出字符串数组。
10. exposure.unit 只是计划报告单位，不是真实源单位。
11. outcome.definition 只有用户已经把研究定义说清楚时才更新。
    如果仅确认了“组合定义”但阈值/组合规则尚不完整，不更新完整 definition。
12. 不生成自然语言回复，不提出下一步问题。

只返回 JSON：
{
  "explicit_updates": [
    {
      "field_path": "字段路径",
      "value": "值",
      "evidence": "用户原话"
    }
  ]
}
"""

        context = {
            "conversation_history": (
                conversation_history[-12:]
            ),
            "current_structured_state": (
                current_state
            ),
            "pending_suggestions": (
                pending_suggestions
            ),
            "latest_user_message": (
                user_message
            ),
        }

        raw = self._request_json(
            system_prompt=system_prompt,
            context=context,
        )

        updates_raw = raw.get(
            "explicit_updates",
            [],
        )

        updates = [
            PlanningStateUpdateV03
            .model_validate(item)
            for item in updates_raw
        ]

        for update in updates:

            if (
                update.field_path
                not in self.ALLOWED_UPDATE_PATHS
            ):
                raise ValueError(
                    "状态解释器返回了不允许更新的字段："
                    f"{update.field_path}"
                )

        return updates

    def compose_reply(
        self,
        *,
        latest_user_message: str,
        conversation_history: list[dict],
        current_state: dict,
        confirmed_fields: list[str],
        discussion_targets: list[str],
    ) -> PlanningAgentTurnV03:
        """
        第二阶段：状态已经更新后再生成回复。

        discussion_targets 由确定性代码计算，
        AI 只能围绕这些目标主动推进。
        """

        system_prompt = """
你是医学科研方案“对话式规划助手”。

用户给一个课题主题后，会和你像正常聊天一样多轮讨论，
最终得到可预览、可确认、可冻结的 Research Plan。

此时后台已经先处理完用户本轮明确决定，
所以 current_structured_state 是“更新后的最新状态”。

你的任务：
- 自然回应用户刚才的决定
- 必要时简短总结已经明确的内容
- 只围绕 discussion_targets 继续推进
- 一次最多主动讨论 1~2 个关键问题
- 必要时给 1~3 个候选方案并解释差异
- 不要像表单，不要一次列一大串问题

绝对规则：

1. confirmed_fields 中的字段已经确认。
   除非用户主动要求修改，否则不得再次主动询问。

2. discussion_targets 是本轮允许主动追问的唯一白名单。
   不得主动追问白名单之外的字段。

3. 如果 discussion_targets 为空：
   不要制造新问题。
   告诉用户核心研究方案已经完整，
   可以预览、继续主动修改或冻结。

4. Research Planning 讨论“科研上应该怎么做”。
   不要为了适配当前平台能力而诱导用户选择某种方法。

5. 禁止说：
   “当前只支持 Logistic，所以建议用 Logistic”
   “当前只支持完整病例，所以请确认完整病例”
   或类似表达。

6. 某种方法科研上合理但平台暂未实现，
   仍然可以正常讨论。
   执行能力由后续 Capability Check 判断。

7. 不进行真实统计计算。
8. 不生成或执行 Python、R、SQL。
9. 不声称已核实真实变量名、实际单位、编码或派生规则。
   这些属于 Data Binding。
10. 不自行确定临床阈值。
    可以给候选并解释，但需要用户确认或明确要求查证。
11. 不暴露 schema、field_path、版本号等内部实现术语。
12. 回复使用自然、专业、简洁中文。
13. 你绝对不能声称“方案已冻结”“已经正式冻结”“冻结完成”。
    冻结是系统命令，只能由确定性 Finalizer 执行。
    如果用户在普通对话里说“冻结”，不要自行宣称成功。

你还可以输出 suggestions。
suggestions 只能针对 discussion_targets 中的字段，
表示“AI 候选建议”，不会自动成为正式决定。

只返回 JSON：
{
  "assistant_message": "展示给用户的自然语言回复",
  "explicit_updates": [],
  "suggestions": [
    {
      "field_path": "字段路径",
      "value": "候选值",
      "label": "候选名称",
      "reason": "候选理由"
    }
  ]
}
"""

        context = {
            "conversation_history": (
                conversation_history[-12:]
            ),
            "latest_user_message": (
                latest_user_message
            ),
            "current_structured_state": (
                current_state
            ),
            "confirmed_fields": (
                confirmed_fields
            ),
            "discussion_targets": (
                discussion_targets
            ),
        }

        raw = self._request_json(
            system_prompt=system_prompt,
            context=context,
        )

        turn = (
            PlanningAgentTurnV03
            .model_validate(raw)
        )

        # compose 阶段不能再修改状态。
        if turn.explicit_updates:
            raise ValueError(
                "compose_reply 不允许产生 explicit_updates。"
            )

        target_set = set(
            discussion_targets
        )

        for suggestion in (
            turn.suggestions
        ):

            if (
                suggestion.field_path
                not in self.ALLOWED_UPDATE_PATHS
            ):
                raise ValueError(
                    "回复生成器返回了不允许建议的字段："
                    f"{suggestion.field_path}"
                )

            if (
                suggestion.field_path
                not in target_set
            ):
                raise ValueError(
                    "回复生成器提出了状态机未允许的讨论字段："
                    f"{suggestion.field_path}"
                )

        return turn

    def safe_compose_reply(
        self,
        **kwargs,
    ) -> PlanningAgentTurnV03:
        """
        回复生成失败时保持会话存活，
        但绝不修改结构化状态。
        """

        try:
            return self.compose_reply(
                **kwargs
            )

        except Exception:
            return PlanningAgentTurnV03(
                assistant_message=(
                    "刚才回复生成出现了临时异常，"
                    "但你已经确认的研究方案状态没有丢失。"
                    "你可以继续说下一步想法，"
                    "或者输入“预览方案”查看当前状态。"
                ),
                explicit_updates=[],
                suggestions=[],
            )

    def safe_interpret_updates(
        self,
        **kwargs,
    ) -> list[PlanningStateUpdateV03]:
        """
        状态解释连续失败时不更新任何字段，
        避免错误写入。
        """

        try:
            return self.interpret_updates(
                **kwargs
            )

        except Exception:
            return []

    def _request_json(
        self,
        *,
        system_prompt: str,
        context: dict,
    ) -> dict:

        last_error = None

        for attempt in range(
            1,
            self.max_attempts + 1,
        ):

            retry_note = ""

            if attempt > 1:
                retry_note = (
                    "\n\n上一次响应为空或 JSON 格式无效。"
                    "这一次必须只返回完整合法 JSON。"
                )

            request_kwargs = {
                "model": "deepseek-flash",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            system_prompt
                            + retry_note
                        ),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            context,
                            ensure_ascii=False,
                        ),
                    },
                ],
                "temperature": 0,
            }

            if attempt < self.max_attempts:
                request_kwargs[
                    "response_format"
                ] = {
                    "type": "json_object"
                }

            try:

                response = (
                    self.client
                    .chat
                    .completions
                    .create(
                        **request_kwargs
                    )
                )

                content = (
                    response
                    .choices[0]
                    .message
                    .content
                )

                if (
                    content is None
                    or not content.strip()
                ):
                    raise RuntimeError(
                        "模型返回空内容。"
                    )

                return self._parse_json(
                    content
                )

            except Exception as exc:
                last_error = exc

        raise RuntimeError(
            "Planning Agent 连续响应失败。"
        ) from last_error

    @staticmethod
    def _parse_json(
        content: str,
    ) -> dict:

        content = content.strip()

        if not content:
            raise RuntimeError(
                "JSON 内容为空。"
            )

        try:
            return json.loads(content)

        except json.JSONDecodeError:
            pass

        cleaned = re.sub(
            r"^\`\`\`(?:json)?\s*",
            "",
            content,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\s*\`\`\`$",
            "",
            cleaned,
        )

        try:
            return json.loads(cleaned)

        except json.JSONDecodeError:
            pass

        start = content.find("{")
        end = content.rfind("}")

        if (
            start != -1
            and end != -1
            and end > start
        ):

            candidate_json = (
                content[
                    start:end + 1
                ]
            )

            try:
                return json.loads(
                    candidate_json
                )

            except json.JSONDecodeError:
                pass

        raise RuntimeError(
            "无法解析模型返回的 JSON：\n"
            + content
        )
