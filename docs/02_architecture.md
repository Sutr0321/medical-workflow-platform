# 02 架构说明

## 1. 总体架构

```text
用户提出研究问题
        ↓
LLM Semantic Extractor
        ↓
Candidate Research Spec
        ↓
Candidate Proposal
        ↓
Generic Review Engine
        ↓
Review Decision Log
        ↓
Frozen Research Plan
        ↓
Data Binding
        ↓
Executable Analysis Spec
        ↓
Rule Engine
        ↓
YAML Template
        ↓
DAG
        ↓
Workflow Engine
        ↓
Algorithm Registry
        ↓
Algorithm Block
        ↓
Result Registry
```

## 2. 为什么从 V0.1 升到 V0.2

V0.1 已完成：

- Candidate Research Spec
- 固定 Validator
- 人工确认
- Freeze / Hash / Store
- Algorithm I/O Contract
- Result Contract

V0.2 进一步拆开三类本质不同的信息。

### Candidate Proposal

给人看的讨论层。

可以保存：

- 当前值
- 理由
- 受控选项
- 自定义输入入口
- provenance

### Review Decision Log

保存人工审核过程：

- 谁审核
- 原始值
- 最终值
- 决策动作
- 时间

### Research Plan

冻结正式研究计划，但还不能直接执行。

只允许明确、标准化、无歧义的语义值。

## 3. LLM 边界

LLM 当前仍只负责：

- 从用户研究问题提取明确表达的信息
- 输出 Candidate Research Spec

LLM 不负责：

- 自动选择统计方法
- 自动确定缺失研究条件
- 自动决定是否冻结
- 生成正式执行 Spec
- 直接统计计算

open issues 和执行层检查仍由固定代码完成。

## 4. Proposal Builder

`ProposalBuilderV02` 把 Candidate Spec 转成面向科研人员的审核项。

每个 Proposal Item 包含：

```text
field_path
title
current_value
reason
options
allow_custom
blocking
provenance
```

它替代了“每个字段手写一个确认函数”的扩展方式。

## 5. Generic Review Engine

`ReviewEngineV02` 接收：

```text
Proposal
+
field_path -> selected_value
```

并输出：

```text
reviewed Candidate
+
ReviewDecisionLogV02
```

以后增加字段时，主要扩展 Schema / Proposal metadata，而不是继续复制大量 CLI if/else。

## 6. Execution Spec

`ResearchPlanV02` 是经人工审核后冻结的正式研究计划。它不包含真实数据列、实际单位、编码或派生表达式，因此不能直接交给算法执行。

当前包含：

- study_design
- objective
- dataset
- population
- exposure
- outcome
- covariates
- missing_data
- analysis

不包含：

- AI 推荐理由
- alternatives
- open issues
- UI 状态
- 真实数据列名

真实列名属于后续 Data Binding。

## 7. Fail Closed

执行层会拒绝明显模糊语义，例如：

```text
待确认
需确认
进一步确认
取决于
视情况
若为横断面
若为队列
可选
```

这类内容可以存在于讨论阶段，但不能进入正式 Execution Spec。

## 8. Artifact 分离

V0.2 一次正式冻结保存：

```text
proposal.json
review_log.json
execution_spec.json
```

后续系统先读取 `research_plan.json`，再通过 Data Binding 绑定真实变量、单位、编码与派生规则，之后才生成 Executable Analysis Spec。

Proposal 和 Review Log 用于：

- 人工回看
- 决策审计
- 解释为什么最终执行值是当前结果

## 9. 下一阶段

完成 V0.2 本地验收后进入：

```text
Frozen Execution Spec
        ↓
Data Binding Contract
        ↓
Rule Engine
        ↓
YAML Template
        ↓
DAG
```

第一条完整闭环仍以：

```text
cross_sectional
+
binary outcome
+
logistic_regression
```

作为最小实现。
