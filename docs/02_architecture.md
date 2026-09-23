# 02 架构说明

## 1. 总体架构

```text
用户给出课题主题
        ↓
Conversational Planning Agent
        ↓
Planning Session
        ↓
Structured Research State
        ↓
Deterministic Validator / Readiness
        ↓
多轮继续对话
        ↓
Research Plan Preview
        ↓
用户最终确认
        ↓
Frozen Research Plan
        ↓
Data Binding
        ↓
Executable Analysis Spec
        ↓
Rule Engine
        ↓
YAML / DAG
        ↓
Workflow Engine
        ↓
Algorithm Registry / Block
        ↓
Result Registry
```

## 2. 用户看到什么

用户主要看到自然语言对话，而不是 JSON 或 field_path。

例如：

```text
用户：
我想研究维生素D与高血压的关系。

AI：
可以。这个课题还需要先确定数据来源和研究设计。
你准备使用什么数据库？
```

用户还可以随时查看“研究方案实时预览”。

## 3. 后台维护什么

每个 `PlanningSessionV03` 保存：

- session_id
- messages
- current_candidate
- confirmed_fields
- decisions
- pending_suggestions
- status
- created_at / updated_at

状态：

```text
DISCUSSING
READY_TO_FREEZE
FROZEN
```

## 4. AI 输出不是直接改数据库

V0.3.1 起，每一轮拆成两个阶段：

```text
用户消息
→ interpret_updates
→ 确定性更新 Research State
→ 重新计算 discussion_targets
→ compose_reply
```

因此回复生成时看到的一定是本轮更新后的状态。

原始 Planning Agent 内部结构仍区分：

```text
assistant_message
explicit_updates
suggestions
```

### explicit_updates

只有用户当前消息已经明确表达的内容才能进入。

例如用户说：

```text
用 NHANES 2017-2018，纳入20岁以上成年人。
```

可以产生明确状态更新。

### suggestions

AI 自己提出的候选方案只能进入 pending suggestions。

已确认字段从 `discussion_targets` 中排除，除非用户主动要求修改，否则 AI 不允许再次主动询问。

例如：

```text
如果最终是横断面 + 二分类结局，
Logistic 回归可以作为一个候选主分析方法。
```

在用户明确接受前，不能写入正式状态。

## 5. 确定性层仍然存在

V0.3 并没有把可靠性重新交给 LLM。

固定程序仍负责：

- Schema 校验
- 允许更新的 field_path
- Pydantic 类型约束
- readiness
- freeze 前完整性检查
- 模糊语义 Fail Closed
- content hash
- immutable Frozen Research Plan

因此：

> 对用户是聊天，对系统是结构化状态机。

另外，Research Plan 与当前执行能力分离。科研人员可以冻结科研上合理但当前执行引擎尚未实现的方案；独立 Capability Checker 只负责报告支持情况，不能反向修改 Research Plan。

## 6. Preview

`ResearchPlanPreviewV03` 从同一结构化状态生成可读预览。

CLI 当前使用文本渲染。

未来 Web UI 可以直接做成：

```text
左侧：AI 对话
右侧：Research Plan 实时预览
底部：确认并冻结研究方案
```

## 7. Freeze

Freeze 不调用 LLM。

只有状态达到：

```text
READY_TO_FREEZE
```

并且用户执行最终确认后，才生成：

```text
FrozenResearchPlanV02
```

冻结后当前版本不允许直接修改。

## 8. Data Binding 边界

Research Plan 只冻结研究意图。

真实数据细节继续留给下一阶段：

- dataset version / source file
- source variable
- actual source unit
- coding
- reference group
- transformation
- derived variable
- derivation rule

完成 Data Binding 后才生成真正的：

```text
Executable Analysis Spec
```

## 9. Artifact

V0.3 冻结后保存：

```text
planning_session.json
transcript.json
review_log.json
research_plan.json
```

这样既保留最终方案，也保留方案是如何通过对话形成的。
