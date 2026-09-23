# 03 项目进度

最后更新：2026-09-23

## 当前稳定基线

```text
v0.1.0-schema-contract
```

## 当前开发分支

```text
feat/conversational-planning-v0.3
```

## 当前阶段

> Conversational Research Planning V0.3

目标：

> 用户给一个课题主题，之后像和 ChatGPT / Codex 一样多轮对话，最终预览并冻结 Research Plan。

## 已实现

| 模块 | 状态 |
|---|---|
| DeepSeek API | ✅ |
| Candidate Research Spec | ✅ |
| Deterministic Validator | ✅ |
| Candidate Updater | ✅ |
| Research Plan / Freeze / Hash | ✅ |
| Planning Session V0.3 | ✅ |
| Conversation Messages | ✅ |
| Confirmed Decision History | ✅ |
| Pending AI Suggestions | ✅ |
| Conversational Planning Agent | ✅ |
| Session Service | ✅ |
| Deterministic Readiness | ✅ |
| Confirmed-field no-repeat rule | ✅ |
| Two-stage turn processing | ✅ |
| Execution Capability Checker | ✅ |
| Research Plan Preview | ✅ |
| Conversational Finalizer | ✅ |
| Transcript / Review Log / Research Plan Store | ✅ |
| V0.3 自动验收脚本 | ✅ |
| V0.3 CLI 对话 Demo | ✅ |

## 待本地验收

```bat
python examples\test_conversational_planning_v03.py
```

通过后运行：

```bat
python examples\run_conversational_planning_v03.py
```

## 尚未完成

| 模块 | 状态 |
|---|---|
| Planning Session 持久化恢复 | ⬜ |
| Web Chat UI | ⬜ |
| Data Binding Contract | ⬜ |
| Executable Analysis Spec | ⬜ |
| Rule Engine | ⬜ |
| YAML Template | ⬜ |
| DAG / Workflow Engine | ⬜ |
| Algorithm Registry | ⬜ |
| Result Registry | ⬜ |
| 真实 Logistic Regression Block | ⬜ |
| Golden Test | ⬜ |

## 当前关键边界

当前 V0.3 已经解决“研究方案如何自然讨论并冻结”，并进一步修复了两类关键问题：

- 用户刚确认的字段不会再次主动询问
- 当前平台实现能力不会反向绑架科研方案选择

但它仍然没有解决“真实数据怎么跑”。

真正跨出 Planning Demo 的下一关键节点仍然是：

```text
Frozen Research Plan
→ Data Binding
→ Executable Analysis Spec
→ 真实 Workflow
→ Golden Test
```
