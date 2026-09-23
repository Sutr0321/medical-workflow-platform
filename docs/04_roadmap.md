# 04 开发路线图

## 总目标

先完成一条可验证的真实闭环：

```text
研究问题
↓
Candidate Research Spec
↓
Candidate Proposal
↓
人工审核
↓
Review Decision Log
↓
Frozen Execution Spec
↓
Data Binding
↓
Rule / YAML
↓
DAG
↓
Workflow
↓
真实 Logistic Regression
↓
Result Registry
↓
Golden Test
```

## Phase 1：Schema Contract V0.1

状态：✅ 已完成

标签：

```text
v0.1.0-schema-contract
```

## Phase 1.5：Research Planning / Review V0.2

状态：⏳ 已开发，等待本地验收

目标：

把“给人讨论的候选建议”和“给机器执行的正式 Spec”分离。

新增：

- CandidateProposalV02
- ProposalItemV02
- ProposalOptionV02
- ReviewDecisionLogV02
- Generic Review Engine
- ExecutionResearchSpecV02
- FrozenExecutionSpecV02
- 模糊语义拦截
- 三文件 artifact bundle

验收：

- Proposal 与 Execution Spec 分离
- 所有人工选择进入 Review Log
- 相同 Execution Spec 产生相同 hash
- Frozen 不可修改
- “待确认/视情况/可选”等不能进入执行层

## Phase 2：Data Binding Contract

状态：⬜

目标：

把正式研究语义映射到真实数据。

例如：

```text
血清25-羟基维生素D
→ LBXVIDMS

高血压
→ 派生变量 hypertension
```

Data Binding 负责：

- dataset version
- source file
- source variable
- derived variable
- unit
- coding
- reference group
- transformation
- derivation rule

原则：

> 不修改 Frozen Execution Spec。

## Phase 3：Rule + YAML Template

状态：⬜

第一版只支持：

```text
cross_sectional
binary outcome
logistic_regression
```

验收：

- 相同 Execution Spec 选择相同模板
- 不调用 LLM
- 不支持组合 Fail Closed

## Phase 4：YAML → DAG

状态：⬜

需要：

- Node / Edge Schema
- DAG Parser
- DAG Validator
- 环检测
- 拓扑排序

## Phase 5：Algorithm Registry + Mock Block

状态：⬜

目标：

Workflow 只能通过 Registry 找算法。

第一版注册：

```text
logistic_regression
```

## Phase 6：Workflow Engine

状态：⬜

第一版：

- 单机
- 串行
- 明确状态
- 错误即停止

## Phase 7：Result Registry

状态：⬜

结果至少关联：

- spec_id
- spec_version
- data_binding_id
- workflow/template version
- algorithm_name
- algorithm_version
- n_used
- estimate
- CI
- P
- timestamp

## Phase 8：真实 Logistic Regression Block

状态：⬜

用真实测试数据执行：

```text
暴露
+
二分类结局
+
协变量
→ OR / 95%CI / P
```

## Phase 9：Golden Test

状态：⬜

固定：

- 测试数据
- Execution Spec
- Data Binding
- 人工标准代码
- 人工标准结果
- 自动结果
- 数值容差

只有通过 Golden Test 的算法版本才允许标记为 validated。

## Phase 10：算法扩展

在闭环稳定后再增加：

- Linear Regression
- Cox Regression
- RCS
- Survey-weighted Regression
- Kaplan-Meier
- Mediation
- Clustering

## Phase 11：Web UI

最后再做：

- 研究问题输入
- Proposal 审核
- Review Log 查看
- Execution Spec 查看
- Workflow 状态
- Result 展示

不在后端闭环稳定前投入复杂前端。
