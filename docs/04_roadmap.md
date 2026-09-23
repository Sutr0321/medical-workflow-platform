# 04 开发路线图

## Phase 1：Schema Contract V0.1

状态：✅

## Phase 1.5：Research Planning / Review V0.2

状态：✅ 已形成底层分层设计

核心：

- Proposal
- Review Log
- Research Plan
- Freeze / Hash

## Phase 1.6：Conversational Research Planning V0.3

状态：⏳ 已开发，等待本地验收

目标：

```text
课题主题
→ 多轮自然语言对话
→ 实时 Research Plan
→ 用户确认
→ Frozen Research Plan
```

验收：

- 用户不需要逐字段填表
- AI 一次优先推进 1–2 个关键问题
- AI 建议不自动写成确认值
- 用户明确表达的决定可更新结构化状态
- 随时可预览 Research Plan
- 不完整方案不能冻结
- 完整方案可确定性冻结
- transcript / review log / research plan 可审计

## Phase 2：Data Binding

状态：⬜

目标：

把 Frozen Research Plan 的研究概念映射到真实数据。

负责：

- dataset version
- source file
- source variable
- actual source unit
- coding
- reference group
- transformation
- derived variable
- derivation rule

产物：

```text
data_binding.json
```

## Phase 3：Executable Analysis Spec

状态：⬜

输入：

```text
Frozen Research Plan
+
Validated Data Binding
```

输出：

```text
Executable Analysis Spec
```

它才是 Rule / Workflow 的正式输入。

## Phase 4：Rule + YAML

状态：⬜

第一条最小闭环：

```text
cross_sectional
+
binary outcome
+
logistic_regression
```

## Phase 5：DAG + Workflow Engine

状态：⬜

## Phase 6：Algorithm Registry

状态：⬜

第一版注册：

```text
logistic_regression
```

## Phase 7：真实 Logistic Regression

状态：⬜

## Phase 8：Result Registry

状态：⬜

## Phase 9：Golden Test

状态：⬜

自动结果必须与人工标准代码在预设容差内一致。

## Phase 10：算法扩展

闭环稳定后再增加：

- Linear Regression
- Cox Regression
- RCS
- Survey-weighted Regression
- Kaplan-Meier
- Mediation
- Clustering

## Phase 11：Web UI

后端会话与冻结机制稳定后，前端目标界面：

```text
┌────────────────────┬────────────────────┐
│ AI 对话             │ Research Plan       │
│                    │ 实时预览             │
│ 用户 / AI 多轮讨论  │ 已确认 / 待讨论      │
│                    │                     │
└────────────────────┴────────────────────┘
          [确认并冻结研究方案]
```

前端只是消费已有 Planning Session / Preview / Freeze API，
不重新实现业务逻辑。
