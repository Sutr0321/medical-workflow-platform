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

    目标：
    - 像正常对话一样讨论研究方案
    - 解释为什么某些问题需要确认
    - 给出有限候选建议
    - 从用户当前消息中提取明确决定
    - 一次只推进少量关键问题

    重要边界：
    - 不做真实统计
    - 不查真实数据列
    - 不把 AI 建议直接写入正式研究状态
    - 只有 explicit_updates 才允许后台落状态
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

    def __init__(self):
        self.client = create_deepseek_client()

    def respond(
        self,
        *,
        user_message: str,
        conversation_history: list[dict],
        current_state: dict,
        missing_fields: list[str],
        pending_suggestions: list[dict],
    ) -> PlanningAgentTurnV03:

        system_prompt = """
你是医学科研方案“对话式规划助手”。

用户会先给一个课题主题，然后与你多轮对话，
直到得到一份可以人工预览、确认并冻结的 Research Plan。

你不是字段填表机器人。
你的回复应该像正常科研讨论：
- 理解用户当前想法
- 简洁总结已经明确的内容
- 解释为什么某个关键问题需要继续明确
- 必要时给出 1~3 个有限候选方案和理由
- 一次优先讨论 1~2 个真正会改变研究方案的问题
- 不要一次抛出十几个问题

但你必须遵守严格边界：

1. 不能进行真实统计计算。
2. 不能生成或执行 Python、R、SQL。
3. 不能声称已经核实真实数据字典、真实列名、单位或编码。
4. 真实 source column、真实 source unit、coding、派生规则属于后续 Data Binding。
5. 不能把常识自动写成用户已经确认的事实。
6. AI 的“建议”只能放在 suggestions。
7. 只有用户在当前消息中明确说出的事实、选择或明确接受的上一轮建议，
   才能放在 explicit_updates。
8. 如果用户只是问“哪个好”“为什么”，不能把建议当作确认。
9. 不允许因为 binary outcome 就自动确认 Logistic。
10. 不允许因为“成年人”自动确认 age_min=18。
11. 不允许自行确定疾病临床阈值。
12. 当前平台只支持第一个最小闭环：
    - study_design = cross_sectional
    - objective = association
    - outcome.data_type = binary
    - analysis.method = logistic_regression
    - missing_data.strategy = complete_case_global
    如果用户想做当前版本尚不支持的方法，可以在自然语言回复中解释，
    但不要伪造系统已经支持。
13. 回复用户时不要展示 JSON、field_path 或内部 schema 名称。
14. assistant_message 使用自然、专业、简洁的中文。
15. 如果已有 pending_suggestions，而用户明确说“可以”“就这个”“按你说的”等，
    可以结合上下文把被接受的建议写入 explicit_updates。
16. covariates 的 explicit_updates 必须使用字符串数组，例如：
    ["年龄", "性别", "BMI"]

内部必须返回 JSON，格式：

{
  "assistant_message": "真正展示给用户的自然语言回复",
  "explicit_updates": [
    {
      "field_path": "字段路径",
      "value": "值",
      "evidence": "用户当前消息中支持这个更新的简短原话"
    }
  ],
  "suggestions": [
    {
      "field_path": "字段路径",
      "value": "候选值",
      "label": "给用户看的名称",
      "reason": "为什么这是合理候选"
    }
  ]
}

如果当前消息没有明确更新，就返回空 explicit_updates。
如果没有需要提出的候选，就返回空 suggestions。
"""

        context = {
            "conversation_history": (
                conversation_history[-12:]
            ),
            "current_structured_state": (
                current_state
            ),
            "missing_fields": (
                missing_fields
            ),
            "pending_suggestions": (
                pending_suggestions
            ),
            "latest_user_message": (
                user_message
            ),
        }

        response = self.client.chat.completions.create(
            model="deepseek-flash",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        context,
                        ensure_ascii=False,
                    ),
                },
            ],
            response_format={
                "type": "json_object"
            },
            temperature=0,
        )

        content = (
            response
            .choices[0]
            .message
            .content
        )

        if not content:
            raise RuntimeError(
                "Planning Agent 返回内容为空。"
            )

        raw = self._parse_json(
            content
        )

        turn = (
            PlanningAgentTurnV03
            .model_validate(raw)
        )

        for update in (
            turn.explicit_updates
        ):

            if (
                update.field_path
                not in self.ALLOWED_UPDATE_PATHS
            ):
                raise ValueError(
                    "Planning Agent 返回了"
                    "不允许更新的字段："
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
                    "Planning Agent 返回了"
                    "不允许建议的字段："
                    f"{suggestion.field_path}"
                )

        return turn

    @staticmethod
    def _parse_json(
        content: str,
    ) -> dict:

        content = content.strip()

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

        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "无法解析 Planning Agent JSON：\n"
                + content
            ) from exc
