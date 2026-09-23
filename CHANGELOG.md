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
- Conversational Planning acceptance test
- Conversational Planning CLI demo

### V0.3 Changed

- 对话处理拆成“状态解释 → 更新 → 重新计算目标 → 回复生成”两阶段
- 已确认字段从下一轮主动讨论目标中排除
- Research Plan 不再被当前 Logistic / complete-case 实现能力限制
- 新增独立 Execution Capability Checker，平台支持性不再反向修改科研方案

- Research Planning 主交互从“逐字段确认”改为“自然语言多轮对话”
- Candidate Research Spec 继续作为后台结构化状态
- AI 建议与用户明确决定严格分离
- Freeze 保持确定性，不由 LLM 决定
- Frozen Research Plan 仍需经过 Data Binding 才能执行

### Planned

- Planning Session persistence / resume
- Data Binding Contract
- Executable Analysis Spec
- Rule Engine
- YAML / DAG
- Workflow Engine
- Algorithm Registry
- Result Registry
- Real Logistic Regression Block
- Golden Test
- Web Chat UI

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
