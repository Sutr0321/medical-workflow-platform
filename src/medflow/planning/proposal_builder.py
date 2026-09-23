import uuid

from medflow.contracts.candidate_spec import (
    CandidateResearchSpecV01,
)
from medflow.contracts.proposal import (
    CandidateProposalV02,
    ProposalItemV02,
    ProposalOptionV02,
)


class ProposalBuilderV02:
    """
    把 Candidate Research Spec 转换成面向科研人员的审核 Proposal。

    这里不调用 LLM。
    Proposal 的作用是：
    1. 把机器字段翻译成人能理解的审核项；
    2. 给出受控选项；
    3. 记录哪些值来自用户明确表达，哪些值仍需要人工补充。

    Proposal 不是 Workflow 的执行输入。
    """

    @staticmethod
    def build(
        spec: CandidateResearchSpecV01,
    ) -> CandidateProposalV02:

        items: list[ProposalItemV02] = []

        def add(
            *,
            field_path: str,
            title: str,
            current_value,
            reason: str,
            options: list[ProposalOptionV02] | None = None,
            allow_custom: bool = False,
            blocking: bool = True,
        ) -> None:

            provenance = (
                "USER_EXPLICIT"
                if current_value not in (None, [])
                else "SYSTEM_REQUIRED"
            )

            items.append(
                ProposalItemV02(
                    field_path=field_path,
                    title=title,
                    current_value=current_value,
                    reason=reason,
                    options=options or [],
                    allow_custom=allow_custom,
                    blocking=blocking,
                    provenance=provenance,
                )
            )

        add(
            field_path="study_design",
            title="研究设计",
            current_value=spec.study_design,
            reason=(
                "研究设计会决定后续可用的统计流程，"
                "必须在执行前明确。"
            ),
            options=[
                ProposalOptionV02(
                    value="cross_sectional",
                    label="横断面研究",
                    description=(
                        "暴露与结局在同一研究时点或同一调查周期评估。"
                    ),
                )
            ],
        )

        add(
            field_path="objective",
            title="研究目的",
            current_value=spec.objective,
            reason=(
                "执行层需要明确主研究目的，"
                "V0.2 第一个闭环当前只支持关联性研究。"
            ),
            options=[
                ProposalOptionV02(
                    value="association",
                    label="关联性研究",
                )
            ],
        )

        add(
            field_path="dataset.name",
            title="数据来源",
            current_value=spec.dataset.name,
            reason=(
                "执行分析前必须明确数据来源；"
                "真实文件路径和真实列名留到 Data Binding 阶段处理。"
            ),
            allow_custom=True,
        )

        add(
            field_path="population.age_min",
            title="最低年龄",
            current_value=spec.population.age_min,
            reason=(
                "年龄下限属于研究人群定义，"
                "不能由模型依据“成年人”等词自动推断。"
            ),
            allow_custom=True,
        )

        add(
            field_path="exposure.name",
            title="主要暴露",
            current_value=spec.exposure.name,
            reason=(
                "主要暴露必须明确，"
                "后续 Data Binding 才能映射到真实变量。"
            ),
            allow_custom=True,
        )

        add(
            field_path="exposure.data_type",
            title="暴露变量类型",
            current_value=spec.exposure.data_type,
            reason=(
                "变量类型会影响模型编码方式和算法输入。"
            ),
            options=[
                ProposalOptionV02(
                    value="continuous",
                    label="连续变量",
                ),
                ProposalOptionV02(
                    value="categorical",
                    label="分类变量",
                ),
                ProposalOptionV02(
                    value="binary",
                    label="二分类变量",
                ),
            ],
        )

        add(
            field_path="exposure.analysis_form",
            title="暴露进入模型的形式",
            current_value=spec.exposure.analysis_form,
            reason=(
                "同一个暴露可以按连续或分类形式进入模型，"
                "这必须由研究方案明确，而不能由算法自行决定。"
            ),
            options=[
                ProposalOptionV02(
                    value="continuous",
                    label="连续形式",
                ),
                ProposalOptionV02(
                    value="categorical",
                    label="分类形式",
                ),
            ],
        )

        add(
            field_path="exposure.unit",
            title="暴露单位",
            current_value=spec.exposure.unit,
            reason=(
                "单位有助于后续解释和数据绑定，"
                "但当前语义方案允许暂不填写。"
            ),
            allow_custom=True,
            blocking=False,
        )

        add(
            field_path="outcome.name",
            title="主要结局",
            current_value=spec.outcome.name,
            reason=(
                "主要结局必须明确，"
                "后续才能映射真实数据列并构造算法输入。"
            ),
            allow_custom=True,
        )

        add(
            field_path="outcome.data_type",
            title="结局变量类型",
            current_value=spec.outcome.data_type,
            reason=(
                "V0.2 第一个执行闭环只支持二分类结局。"
            ),
            options=[
                ProposalOptionV02(
                    value="binary",
                    label="二分类结局",
                )
            ],
        )

        add(
            field_path="outcome.definition",
            title="结局判定标准",
            current_value=spec.outcome.definition,
            reason=(
                "结局定义直接决定样本如何被编码，"
                "禁止使用“待确认”“视情况而定”等模糊描述进入执行层。"
            ),
            allow_custom=True,
        )

        add(
            field_path="missing_data.strategy",
            title="缺失值处理",
            current_value=spec.missing_data.strategy,
            reason=(
                "缺失数据处理属于预先指定的分析决策。"
            ),
            options=[
                ProposalOptionV02(
                    value="complete_case_global",
                    label="完整病例分析",
                )
            ],
        )

        add(
            field_path="analysis.method",
            title="主分析方法",
            current_value=spec.analysis.method,
            reason=(
                "统计方法必须由研究人员确认；"
                "不能仅因为结局为二分类就由 LLM 自动选择 Logistic 回归。"
            ),
            options=[
                ProposalOptionV02(
                    value="logistic_regression",
                    label="Logistic 回归",
                )
            ],
        )

        add(
            field_path="covariates",
            title="协变量",
            current_value=[
                item.name
                for item in spec.covariates
            ],
            reason=(
                "协变量属于研究方案的一部分。"
                "V0.2 只保存确认后的协变量名称；"
                "真实列名、编码和参考组放到 Data Binding。"
            ),
            allow_custom=True,
            blocking=False,
        )

        return CandidateProposalV02(
            proposal_id=(
                "RP-"
                + uuid.uuid4().hex[:12].upper()
            ),
            source_question=spec.source_question,
            candidate_spec=spec,
            items=items,
        )
