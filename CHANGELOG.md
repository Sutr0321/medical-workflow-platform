# Changelog

## [Unreleased]

### V0.3 Added

- PlanningSessionV03
- PlanningMessageV03
- PlanningDecisionV03
- PlanningSuggestionV03
- PlanningAgentTurnV03
- ConversationalPlanningAgentV03
- PlanningSessionServiceV03
- ConversationalReadinessV03
- ResearchPlanPreviewV03
- ConversationalPlanningFinalizerV03
- ConversationPlanningStoreV03
- Execution Capability Checker
- Conversational Planning acceptance test
- Conversational Planning CLI demo
- Rich Research Plan V0.3
- NHANES cycle readiness rule
- deterministic command routing for preview / freeze / quit / send
- deterministic system normalization audit record

### V0.3 Changed

- 对话处理拆成“解释用户明确决策 → 更新结构化状态 → 重新计算目标 → 回复生成”两阶段
- 已确认字段从下一轮主动讨论目标中排除
- Research Plan 不再被当前 Logistic / complete-case 实现能力限制
- AI suggestion 与用户明确决定分离
- Freeze 保持确定性，不由 LLM 决定
- NHANES 调查周期属于研究范围时，未确定周期不能进入 READY_TO_FREEZE
- 当上游研究决策已明确时，可执行不改变研究意图的确定性文本规范化，并记录 SYSTEM_NORMALIZATION
- Planning Agent 不再允许凭模型记忆把数据库变量、文件、测量规程或权重规则当成已验证事实
- Rich Research Plan 将主模型、效应量、CI、复杂抽样、次要分析、敏感性分析和缺失值条件策略分开保存

### V0.3 Acceptance

已完成端到端人工验收：

```text
完整研究方案
→ Conversational Planning
→ 缺失周期被阻断
→ 用户补充 NHANES 周期
→ READY_TO_FREEZE
→ Preview
→ 人工确认
→ Frozen Research Plan V0.3
→ JSON 落盘
```

已验证 Frozen JSON 保留：

- dataset version / cycles
- outcome definition
- outcome sensitivity definitions
- missing-data strategy / mode / assessment / decision rule / sensitivity plan
- primary model
- effect measure
- CI level
- survey design requirement
- secondary analyses
- sensitivity analyses
- plan id / version / content hash

### Current Stop Point

第一阶段开发主线当前停止在：

```text
Step 1 Schema Contract                    ✅
└─ Conversational Research Planning V0.3 ✅

Step 2 Simple YAML                        ⬅️ NEXT
```

当前不继续扩展聊天 Demo。

### Planned Development Order

1. Simple YAML Workflow
2. YAML → DAG
3. Mock Algorithms
4. Workflow Engine
5. Algorithm Registry
6. Result Registry
7. Replace one Mock with one real algorithm
8. Data Binding / Executable Analysis Spec 在真实数据执行前补齐并接入

## [v0.1.0-schema-contract] - 2026-09-23

### Added

- DeepSeek API Client
- Candidate Research Spec
- Deterministic Validator
- Candidate Updater
- Readiness Checker
- Human Review Service
- Frozen Research Spec
- Research Spec ID / Version / Hash
- Algorithm I/O Schema
- Result Schema
- Schema Contract tests
