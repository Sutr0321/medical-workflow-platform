# Changelog

本文件记录项目重要阶段变化。

## [Unreleased]

### Planned

- Rule Engine V0.1
- YAML Template V0.1
- YAML → DAG
- DAG Validator
- Algorithm Registry
- Mock Logistic Block
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

### Current Scope

- V0.1 supports Logistic Regression only as the first algorithm contract example
- Real statistical computation is not implemented yet
- Workflow Engine is not implemented yet
