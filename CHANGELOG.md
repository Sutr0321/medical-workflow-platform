# Changelog

## [Unreleased]

### Added

- Candidate Proposal V0.2
- Proposal Item / Option Contract
- Generic Review Engine V0.2
- Review Decision Log V0.2
- Execution Research Spec V0.2
- Frozen Execution Spec V0.2
- Fuzzy semantic Fail-Closed check
- Proposal / Review Log / Execution Spec bundle store
- Research Planning V0.2 acceptance test
- Research Planning V0.2 interactive demo

### Changed

- 将“候选建议层”和“机器执行层”分离
- 后续 Rule / Workflow 只允许读取 Frozen Execution Spec
- 将真实数据列名明确推迟到 Data Binding 阶段
- 协作路线调整为先完成 V0.2，再进入 Data Binding / Rule / YAML

### Planned

- Data Binding Contract
- Rule Engine
- YAML Template
- YAML → DAG
- DAG Validator
- Algorithm Registry
- Workflow Engine
- Result Registry
- Real Logistic Regression Block
- Golden Test

## [v0.1.0-schema-contract] - 2026-09-23

### Added

- DeepSeek API Client
- Natural language → Candidate Research Spec
- Candidate Research Spec Pydantic Schema
- Candidate fixed Validator
- open issues
- Candidate updater
- Readiness checker
- Human review service
- Reviewed Research Spec
- Frozen Research Spec
- Research Spec ID and version
- SHA-256 content hash
- Frozen JSON store
- Algorithm Input Schema
- Algorithm Output Schema
- Algorithm Estimate Schema
- Result Record Schema
- Research Spec interactive Demo
- Schema Contract test script

### Verified

- Incomplete Research Spec cannot be confirmed
- Same Research Spec content produces stable content hash
- Frozen Research Spec cannot be directly modified
- Existing Frozen V1 file cannot be overwritten
- Invalid P value is rejected
- Missing required algorithm input is rejected
- Invalid sample size is rejected
- Invalid spec version is rejected
