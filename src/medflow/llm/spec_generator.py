import json
import re

from medflow.contracts.candidate_spec import (
    CandidateResearchSpecV01,
)

from medflow.llm.client import (
    create_deepseek_client,
)

from medflow.spec.candidate_validator import (
    CandidateSpecValidator,
)


class ResearchSpecGenerator:
    """
    使用 DeepSeek 将自然语言研究问题整理成
    Candidate Research Spec。

    LLM 只负责语义提取。

    open_issues 不由 LLM 决定，
    必须由固定 CandidateSpecValidator 生成。
    """

    def __init__(self):
        self.client = create_deepseek_client()

    def generate(
        self,
        question: str,
    ) -> CandidateResearchSpecV01:

        question = question.strip()

        if not question:
            raise ValueError(
                "研究问题不能为空。"
            )

        system_prompt = """
你是医学研究方案结构化助手。

你的唯一任务是：

把用户已经明确表达的研究信息，
一次性、尽可能完整地整理成指定 JSON 结构。

用户第一条消息可能只是一个简短课题，
也可能已经是一份很丰富的研究方案提示词。
如果用户在同一条消息里已经明确了研究设计、数据集、人群、
暴露类型与分析形式、结局类型与定义、协变量、缺失值策略、
主分析方法等多个决策，必须全部提取，不能故意留空后再追问。

你不能替用户设计研究方案，
不能自行选择统计方法，
不能自行填写用户没有表达的信息。

必须严格遵守以下规则：

1. 不允许编造信息。

2. 用户没有明确表达的信息必须填写 null。

3. 不要根据常识补充年龄。
例如：
“成年人”不能自动转换成 age_min = 18。

4. 不要自行猜测变量单位。

5. 不要自行猜测数据集。

6. 不要自行猜测真实数据列名。

7. 不要自行猜测变量编码。

8. 不要自行定义疾病或结局判定标准。

9. study_design：
只有用户明确说明研究设计时才能填写。
使用稳定的机器可读英文标识，例如：
"cross_sectional"
"cohort"
"case_control"
"randomized_trial"

用户没有明确说明时必须为 null。

10. objective：
如果用户明确表达：
“关系”
“关联”
“相关”
“association”
等关联性研究目标，
可以填写：
"association"

否则填写 null。

11. exposure.data_type：

只有用户明确说明暴露变量是连续变量、
分类变量或二分类变量时才填写。

可选：
"continuous"
"categorical"
"binary"

否则 null。

12. exposure.analysis_form：

只有用户明确说明暴露变量以连续形式
或者分类形式进入模型时才填写。

可选：
"continuous"
"categorical"

否则 null。

13. outcome.name：

只填写“结局本身”的名称，不要把研究关系或研究目的混进名称。

例如：
“血清尿酸与高血压患病状态的关联”
→ outcome.name = "高血压患病状态"

“维生素D与抑郁症状的关系”
→ outcome.name = "抑郁症状"

不要输出：
“高血压患病状态的关联”
“抑郁症状的关系”

13.1 outcome.data_type：

只有用户明确说明结局类型时才填写。
使用稳定机器可读标识，例如：
"binary"
"continuous"
"time_to_event"
"count"

否则 null。

14. missing_data：

只有用户明确说明缺失值处理策略时才填写。

如果用户明确给的是固定策略：
- strategy 填稳定标识，例如 complete_case_global / multiple_imputation
- mode = "fixed"

如果用户明确给的是“评估驱动/条件式”策略：
- strategy 填简洁的人类可读总策略，例如 "评估驱动条件策略"
- mode = "data_dependent"
- assessment 提取用户明确说要评估的内容
- decision_rule 提取用户明确的条件分流规则
- sensitivity_plan 提取用户明确的敏感性分析原则

如果用户没有明确说明，对应字段保持 null 或空数组。
不要因为当前平台实现能力替用户选择。

15. analysis：

只有用户明确说明统计分析计划时才填写。

analysis.method 只记录主模型，使用稳定机器可读标识，例如：
Logistic 回归 → "logistic_regression"
线性回归 → "linear_regression"
Cox 回归 → "cox_regression"
Survey-weighted Logistic → "survey_logistic_regression"

如果用户明确说明：
- OR / PR / beta 等，写入 effect_measure
- 95% CI，写入 ci_level = 0.95
- 复杂抽样 / survey design，写入 survey_design_required = true
- RCS 等补充分析，写入 secondary_analyses
- 稳健方差 Poisson、替代模型等敏感性分析，写入 sensitivity_analyses

绝对禁止因为结局变量类型自行推断统计方法，
也禁止因为平台当前实现能力替用户选择。

16. covariates：

只提取用户明确说明需要调整、
校正或纳入模型的协变量。

每个协变量至少填写 name。

column、data_type、unit、
reference_value 在用户没有明确说明时
必须填写 null。

17. open_issues：

必须始终返回空数组 []。

open_issues 后续由固定程序重新生成，
不是由你判断。

18. 只能返回 JSON。

不要输出 Markdown。
不要输出 ```json。
不要解释。
不要添加任何额外文本。

JSON 必须符合以下结构：

{
  "schema_version": "0.1.1",
  "source_question": "原始研究问题",
  "study_design": null,
  "objective": null,

  "dataset": {
    "name": null,
    "version": null,
    "local_path": null
  },

  "population": {
    "description": null,
    "age_min": null,
    "age_max": null
  },

  "exposure": {
    "name": null,
    "column": null,
    "data_type": null,
    "unit": null,
    "analysis_form": null
  },

  "outcome": {
    "name": null,
    "column": null,
    "data_type": null,
    "coding": {
      "negative_value": null,
      "positive_value": null
    },
    "definition": null,
    "sensitivity_definitions": []
  },

  "covariates": [],

  "missing_data": {
    "strategy": null,
    "mode": null,
    "assessment": [],
    "decision_rule": null,
    "sensitivity_plan": null
  },

  "analysis": {
    "method": null,
    "effect_measure": null,
    "ci_level": null,
    "survey_design_required": null,
    "secondary_analyses": [],
    "sensitivity_analyses": []
  },

  "open_issues": []
}
"""

        user_prompt = f"""
请根据规则整理下面的研究问题：

{question}
"""

        response = self.client.chat.completions.create(
            model="deepseek-flash",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
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
                "DeepSeek 返回内容为空。"
            )

        data = self._parse_json(
            content
        )

        # 强制使用真实原始问题，
        # 不允许 LLM 改写 source_question。
        data["source_question"] = question

        # open_issues 完全不信任 LLM。
        data["open_issues"] = []

        candidate = (
            CandidateResearchSpecV01.model_validate(
                data
            )
        )

        # 使用固定程序重新生成 open issues。
        candidate.open_issues = (
            CandidateSpecValidator.validate(
                candidate
            )
        )

        return candidate

    @staticmethod
    def _parse_json(
        content: str,
    ) -> dict:

        content = content.strip()

        # --------------------------------------
        # 第一种情况：
        # DeepSeek 直接返回纯 JSON
        # --------------------------------------

        try:
            return json.loads(
                content
            )

        except json.JSONDecodeError:
            pass

        # --------------------------------------
        # 第二种情况：
        # 模型错误地套了 Markdown code fence
        # --------------------------------------

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
            return json.loads(
                cleaned
            )

        except json.JSONDecodeError:
            pass

        # --------------------------------------
        # 第三种情况：
        # 尝试提取第一个完整 JSON object
        # --------------------------------------

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
            "无法解析 DeepSeek 返回的 JSON：\n"
            + content
        )