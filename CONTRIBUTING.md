# 协作开发规范

本项目目前以小团队协作为主，目标是在保持开发速度的同时，确保 main 分支始终可运行、可追踪。

## 1. 基本原则

### main 只保存稳定版本

不要直接在 main 上进行大功能开发。

main 应满足：

- 当前测试能够运行
- 不包含 API Key
- 不包含明显调试垃圾
- 已完成的功能有基本验收

### 每个任务使用独立分支

新功能：

```text
feat/<功能名>
```

例如：

```text
feat/rule-engine
feat/yaml-template
feat/dag
feat/logistic-block
```

Bug：

```text
fix/<问题名>
```

文档：

```text
docs/<内容>
```

## 2. 推荐开发流程

```text
main
 ↓
创建 Issue
 ↓
建立 feat/* 分支
 ↓
编码
 ↓
本地测试
 ↓
commit
 ↓
push
 ↓
Pull Request
 ↓
另一位成员检查
 ↓
合并 main
```

## 3. 开始新任务

先更新本地 main：

```bat
git checkout main
git pull origin main
```

建立分支：

```bat
git checkout -b feat/rule-engine
```

## 4. Commit 规范

推荐使用：

```text
feat: 新功能
fix: 修复问题
test: 测试
docs: 文档
refactor: 重构
chore: 工程配置
```

示例：

```text
feat: add rule engine v0.1
test: add rule engine validation
docs: update project progress
fix: reject unsupported workflow type
```

## 5. Pull Request 要写什么

至少写：

### 做了什么

例如：

```text
增加 Rule Engine V0.1。
```

### 为什么做

例如：

```text
让 Frozen Research Spec 通过固定规则选择 YAML Template。
```

### 怎么测试

例如：

```text
python examples\test_rule_engine.py
```

### 验收结果

例如：

```text
PASS: supported spec matched logistic template
PASS: unsupported spec failed closed
```

## 6. 两人推荐分工

### 平台工程侧

重点负责：

- Schema
- Rule Engine
- YAML
- DAG
- Workflow Engine
- Registry
- 系统集成

### 医学统计侧

重点负责：

- 统计方法规范
- 算法输入要求
- 算法结果定义
- 人工标准代码
- Golden Test
- 结果一致性验证

这只是推荐分工，不是硬性限制。

## 7. Issue 规范

每个较大的功能建一个 Issue。

Issue 至少写：

```text
目标
范围
不做什么
实现思路
验收标准
```

例如：

```text
Title:
Implement Rule Engine V0.1

目标：
根据 Frozen Research Spec 选择 YAML Template。

范围：
只支持 cross-sectional + binary + logistic。

不做：
不支持 Cox、RCS。

验收：
相同 Spec 稳定匹配同一模板；
不支持组合必须 Fail Closed。
```

## 8. API Key 和敏感信息

禁止提交：

- .env
- API Key
- Token
- 密码
- 私有数据库凭据

当前 `.gitignore` 已包含：

```text
.env
.venv/
.idea/
__pycache__/
*.pyc
.pytest_cache/
```

如果 API Key 曾经被提交，即使后来删除，也应立即旋转密钥。

## 9. artifacts

当前 `artifacts/specs/` 中保存 Demo Frozen Research Spec。

正式处理真实科研数据后，需要重新制定数据安全策略。

原则：

- 不向 GitHub 提交真实敏感患者数据
- 不提交受限数据库原始数据
- 不提交个人身份信息
- 测试尽量使用模拟或公开样例数据

## 10. 修改架构前先讨论

下列内容修改前建议先通过 Issue 或讨论确认：

- Research Spec 字段
- Algorithm Contract
- Result Contract
- Workflow 状态模型
- Algorithm Registry 接口
- 版本策略

因为这些属于跨模块 Contract，修改后可能影响多人代码。
