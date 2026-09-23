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
整理成指定 JSON 结构。

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
只有用户明确说明是横断面研究时，
才能填写：
"cross_sectional"

否则必须为 null。

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

13. outcome.data_type：

当前系统只支持 binary。

只有用户明确说明结局是二分类结局时，
才能填写：
"binary"

否则 null。

14. missing_data.strategy：

只有用户明确说明采用完整病例分析、
complete case analysis
或者同义表达时，
才填写：

"complete_case_global"

否则 null。

15. analysis.method：

只有用户明确说明使用 Logistic 回归、
Logistic regression、
多变量 Logistic 回归、
多因素 Logistic 回归等明确表达时，

才填写：

"logistic_regression"

如果用户没有明确说明具体分析方法，
必须填写 null。

绝对禁止因为结局变量是二分类变量，
就自行推断 Logistic 回归。

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
  "schema_version": "0.1.0",
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
    "definition": null
  },

  "covariates": [],

  "missing_data": {
    "strategy": null
  },

  "analysis": {
    "method": null
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