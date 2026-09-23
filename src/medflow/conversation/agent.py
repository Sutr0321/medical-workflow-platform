import json
import re

from medflow.contracts.planning_session import (
    PlanningAgentTurnV03,
)
from medflow.llm.client import (
    create_deepseek_client,
)


class ConversationalPlanningAgentV03:
    """
    对话式科研方案规划 Agent。

    用户看到自然语言讨论；
    后台只接受用户明确表达或明确接受的结构化更新。

    确定性状态机负责决定“还能问什么”；
    LLM 负责“怎么自然地问、怎么解释”。
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

    def respond(
        self,
        *,
        user_message: str,
        conversation_history: list[dict],
        current_state: dict,
        confirmed_fields: list[str],
        discussion_targets: list[str],
        pending_suggestions: list[dict],
    ) -> PlanningAgentTurnV03:

        system_prompt = """
你是医学科研方案“对话式规划助手”。

用户会先给一个课题主题，然后与你多轮讨论，
最终得到一份可预览、可人工确认、可冻结的 Research Plan。

你的交互应该像正常科研讨论，而不是表单或软件说明书。

你要做：
- 理解上下文
- 简洁总结本轮用户刚刚确认或修改了什么
- 围绕真正尚未解决的问题继续讨论
- 必要时提出 1~3 个有限候选方案，并解释区别
- 每轮最多主动推进 1~2 个关键问题
- 如果用户已经把某项说清楚，不重复询问

最重要的状态规则：

1. confirmed_fields 中的字段视为已经确认。
   除非用户主动要求修改，否则禁止再次主动询问。

2. discussion_targets 是“本轮允许主动追问”的字段白名单。
   你只能主动追问其中的字段。
   不得因为自己觉得某个话题重要，就重新追问已确认字段。

3. 如果 discussion_targets 为空，
   不要制造新问题。
   可以提示用户方案核心内容已完整，可预览或继续主动修改。

4. 用户如果主动提出修改已确认字段，
   可以生成 explicit_updates 更新它。

研究设计边界：

5. Research Planning 讨论“科研上应该怎么做”，
   不要为了迁就当前平台已经实现的算法能力而引导用户做某种选择。

6. 不要说：
   “因为当前平台只支持 Logistic，所以建议你选 Logistic”
   或
   “当前只支持完整病例，所以请确认完整病例”。

7. 如果某种研究方法科研上合理，就正常讨论并记录。
   当前平台能否自动执行，应由后续 Capability Check 判断，
   不属于这一轮科研方案讨论。

8. 不能进行真实统计计算。

9. 不能生成或执行 Python、R、SQL。

10. 不能声称已经核实真实数据字典、真实列名、实际单位或编码。
    真实 source column、source unit、coding、reference group、
    transformation、derivation rule 属于后续 Data Binding。

11. 不允许自行确定疾病临床阈值。
    可以给出候选并解释，但最终必须由用户确认或由用户明确要求查证后再决定。

12. 不允许因为“成年人”自动确认 age_min=18。

13. AI 自己提出的方案只能放 suggestions。
    不能因为“通常这样做”就写入 explicit_updates。

14. 只有以下两类内容可以进入 explicit_updates：
    - 用户当前消息明确表达的决定
    - 用户明确接受的上一轮建议，例如“就第3种”“按你说的”

15. 用户可以用“1”“2”“3”“第3种”“就这个”等简短方式回应。
    必须结合最近上下文理解。

16. outcome.definition 只有在研究定义已经足够明确时才更新。
    如果用户只是确认一个方向，但阈值或组合规则还没说清楚，
    继续讨论，不要伪装成已经完整。

17. exposure.unit 在 Research Planning 阶段只是计划报告单位。
    真实数据源单位留到 Data Binding 核对。

18. covariates 的 explicit_updates 必须是字符串数组。

19. assistant_message 不要展示 JSON、field_path、schema、V0.1/V0.2/V0.3 等内部实现术语，
    除非用户主动询问技术实现。

内部必须返回 JSON：

{
  "assistant_message": "展示给用户的自然语言回复",
  "explicit_updates": [
    {
      "field_path": "字段路径",
      "value": "值",
      "evidence": "支持该更新的用户原话"
    }
  ],
  "suggestions": [
    {
      "field_path": "字段路径",
      "value": "候选值",
      "label": "给用户看的名称",
      "reason": "为什么是合理候选"
    }
  ]
}

如果没有明确更新，explicit_updates 返回 []。
如果没有候选建议，suggestions 返回 []。
只返回 JSON，不要输出 Markdown。
"""

        context = {
            "conversation_history": (
                conversation_history[-12:]
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
            "pending_suggestions": (
                pending_suggestions
            ),
            "latest_user_message": (
                user_message
            ),
        }

        for attempt in range(
            1,
            self.max_attempts + 1,
        ):

            retry_note = ""

            if attempt > 1:
                retry_note = (
                    "\n\n上一次响应为空或格式无效。"
                    "这次必须只返回一个完整合法 JSON object。"
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
                        "Planning Agent 返回空内容。"
                    )

                raw = self._parse_json(
                    content
                )

                turn = (
                    PlanningAgentTurnV03
                    .model_validate(raw)
                )

                self._validate_turn(
                    turn=turn,
                    confirmed_fields=confirmed_fields,
                    discussion_targets=discussion_targets,
                )

                return turn

            except Exception:
                continue

        return PlanningAgentTurnV03(
            assistant_message=(
                "刚才模型响应出现了临时异常，"
                "这一轮没有修改研究方案。"
                "请把你刚才的意思再说一遍即可。"
            ),
            explicit_updates=[],
            suggestions=pending_suggestions,
        )

    def _validate_turn(
        self,
        *,
        turn: PlanningAgentTurnV03,
        confirmed_fields: list[str],
        discussion_targets: list[str],
    ) -> None:

        confirmed = set(
            confirmed_fields
        )

        targets = set(
            discussion_targets
        )

        for update in (
            turn.explicit_updates
        ):

            if (
                update.field_path
                not in self.ALLOWED_UPDATE_PATHS
            ):
                raise ValueError(
                    "Planning Agent 返回了不允许更新的字段："
                    f"{update.field_path}"
                )

        for suggestion in (
            turn.suggestions
        ):

            if (
                suggestion.field_path
                not in self.ALLOWED_UPDATE_PATHS
            ):
                raise ValueError(
                    "Planning Agent 返回了不允许建议的字段："
                    f"{suggestion.field_path}"
                )

            # 已确认字段不能再作为“主动建议主题”。
            if (
                suggestion.field_path
                in confirmed
                and suggestion.field_path
                not in targets
            ):
                raise ValueError(
                    "Planning Agent 对已确认字段重复提出建议："
                    f"{suggestion.field_path}"
                )

            # 正常情况下，建议也应围绕确定性 target。
            if (
                targets
                and suggestion.field_path
                not in targets
            ):
                raise ValueError(
                    "Planning Agent 提出了状态机未允许的讨论字段："
                    f"{suggestion.field_path}"
                )

    @staticmethod
    def _parse_json(
        content: str,
    ) -> dict:

        content = content.strip()

        if not content:
            raise RuntimeError(
                "Planning Agent JSON 内容为空。"
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
            "无法解析 Planning Agent JSON：\n"
            + content
        )
