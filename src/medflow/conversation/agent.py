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
    - 单次模型响应异常时不让整个 Planning Session 崩溃
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

不要向用户暴露内部 schema_version、field_path、
Candidate Spec、V0.1 等实现细节。
除非用户主动询问版本，否则自然讨论研究方案即可。

必须遵守以下边界：

1. 不能进行真实统计计算。
2. 不能生成或执行 Python、R、SQL。
3. 不能声称已经核实真实数据字典、真实列名、实际单位或编码。
4. 真实 source column、真实 source unit、coding、reference group、
   transformation、derivation rule 属于后续 Data Binding。
5. 不能把常识自动写成用户已经确认的事实。
6. AI 自己提出的候选建议只能放在 suggestions。
7. 只有用户在当前消息中明确说出的事实、选择，
   或明确接受的上一轮建议，才能放在 explicit_updates。
8. 如果用户只是问“哪个好”“为什么”，不能把建议当作确认。
9. 不允许因为 binary outcome 就自动确认 Logistic。
10. 不允许因为“成年人”自动确认 age_min=18。
11. 不允许自行确定疾病临床阈值。
12. 当前平台第一个最小执行闭环只支持：
    - study_design = cross_sectional
    - objective = association
    - outcome.data_type = binary
    - analysis.method = logistic_regression
    - missing_data.strategy = complete_case_global
    如果用户想做当前尚未支持的方法，可以自然解释，
    但不能伪装成已经支持。
13. assistant_message 使用自然、专业、简洁的中文。
14. 如果已有 pending_suggestions，而用户明确说
    “可以”“就这个”“按你说的”“选第3种”等，
    可以结合上下文把被接受的建议写入 explicit_updates。
15. 如果用户用“1、2、3”“第3种”“选2”等方式回应，
    必须结合最近一轮对话中的编号选项理解，
    不要要求用户机械重复整段文字。
16. covariates 的 explicit_updates 必须使用字符串数组，例如：
    ["年龄", "性别", "BMI"]
17. outcome.definition 只有在定义已经足够明确时才写入 explicit_updates。
    如果用户只确认“采用组合定义”，但血压阈值、测量规则等仍未明确，
    可以先在自然语言中记录方向并继续追问，
    不要假装完整定义已经确认。
18. exposure.unit 在当前阶段只能表示研究者计划采用的报告单位，
    不能声称是真实数据源单位。

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
只返回 JSON，不要输出 Markdown code fence。
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

        last_error: Exception | None = None

        for attempt in range(
            1,
            self.max_attempts + 1,
        ):

            retry_note = ""

            if attempt > 1:
                retry_note = (
                    "\n\n重要：上一次接口返回为空或格式无效。"
                    "这一次必须只返回一个完整、合法的 JSON object，"
                    "不要返回空字符串，不要输出 Markdown。"
                )

            messages = [
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
            ]

            request_kwargs = {
                "model": "deepseek-flash",
                "messages": messages,
                "temperature": 0,
            }

            # 前两次优先使用 JSON mode。
            # 最后一次取消 response_format，
            # 防止某些瞬时 JSON-mode 异常导致空内容。
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

                self._validate_paths(
                    turn
                )

                return turn

            except Exception as exc:
                last_error = exc

        # 连续多次异常时不让整段会话崩溃。
        # 不做任何状态更新，并保留上一轮 suggestions，
        # 让用户可以直接重述上一条选择。
        return PlanningAgentTurnV03(
            assistant_message=(
                "刚才模型响应出现了临时异常，"
                "这一轮没有修改研究方案。"
                "请把你刚才的选择再说一遍即可；"
                "例如“采用第3种定义，结局按二分类”。"
            ),
            explicit_updates=[],
            suggestions=pending_suggestions,
        )

    def _validate_paths(
        self,
        turn: PlanningAgentTurnV03,
    ) -> None:

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
            r"^```(?:json)?\s*",
            "",
            content,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\s*```$",
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
