# 03 项目进度

最后更新：2026-09-24

## 当前稳定基线

```text
v0.1.0-schema-contract
```

## 当前开发分支

```text
feat/conversational-planning-v0.3
```

## 当前停止点

> **Step 1 已完成。现在停止继续扩 Research Planning，下一步进入 Step 2：Simple YAML。**

```text
第 1 步  Schema Contract                    ✅
         └─ Conversational Planning V0.3    ✅ 主链路验收通过

第 2 步  Simple YAML                        ⬅️ NEXT
第 3 步  YAML → DAG                         ⬜
第 4 步  Mock Algorithms                    ⬜
第 5 步  Workflow Engine                    ⬜
第 6 步  Algorithm Registry                 ⬜
第 7 步  Result Registry                    ⬜
第 8 步  Replace One Real Algorithm         ⬜
```

## Step 1 已完成内容

| 模块 | 状态 |
|---|---|
| DeepSeek API Client | ✅ |
| Candidate Research Spec | ✅ |
| Pydantic Schema Validation | ✅ |
| Deterministic Validator | ✅ |
| Candidate Updater | ✅ |
| Algorithm Input Schema | ✅ |
| Algorithm Output Schema | ✅ |
| Algorithm Estimate Schema | ✅ |
| Result Schema | ✅ |
| Research Plan / Freeze / Hash | ✅ |
| Planning Session V0.3 | ✅ |
| Conversation Messages | ✅ |
| Confirmed Decision History | ✅ |
| Pending AI Suggestions | ✅ |
| Conversational Planning Agent | ✅ |
| Two-stage turn processing | ✅ |
| Deterministic Readiness | ✅ |
| Confirmed-field no-repeat rule | ✅ |
| NHANES cycle readiness rule | ✅ |
| Research Plan Preview | ✅ |
| Deterministic Finalizer | ✅ |
| Transcript / Review Log / Research Plan Store | ✅ |
| Execution Capability Checker | ✅ |
| Command Router | ✅ |
| System Normalization Audit | ✅ |
| V0.3 CLI Demo | ✅ |

## V0.3 人工验收结果

已实际完成：

```text
完整 NHANES 研究方案
→ 自动结构化
→ 周期缺失被识别为 blocking
→ 用户补充 2013–2014 / 2015–2016 / 2017–2018
→ READY_TO_FREEZE
→ Preview
→ 用户确认
→ Frozen Rich Research Plan V0.3
→ JSON 落盘
```

并已检查 `research_plan.json`，确认以下内容没有在冻结过程中丢失：

- dataset version / cycles
- outcome definition
- sensitivity definitions
- covariates
- missing-data strategy / mode / assessment / decision rule / sensitivity plan
- primary model
- effect measure
- 95% CI
- survey design requirement
- RCS
- Poisson / PR sensitivity analysis
- plan id / version / content hash

## 当前明确没有实现

| 模块 | 状态 |
|---|---|
| Simple YAML Workflow | ⬜ |
| YAML Reader | ⬜ |
| YAML Workflow Schema | ⬜ |
| DAG | ⬜ |
| Topological Sort | ⬜ |
| Cycle Detection | ⬜ |
| Mock Algorithms | ⬜ |
| Workflow Engine | ⬜ |
| Algorithm Registry | ⬜ |
| Result Registry | ⬜ |
| Data Binding Contract | ⬜ |
| Executable Analysis Spec | ⬜ |
| Real Logistic Regression | ⬜ |
| Golden Test | ⬜ |
| Web Chat UI | ⬜ |

## 下一步：Step 2

下一步只完成：

```text
Simple YAML
→ YAML Reader
→ Pydantic Validation
```

第一版场景：

```text
横断面研究 + 二分类结局
```

流程：

```text
数据准备 → 基线表 → Logistic → RCS
```

验收标准：

1. 程序能正确读取 YAML。
2. 能读到每个 step 的 id。
3. 能读到 `depends_on`。
4. 能读到 algorithm id 和 version。
5. 缺失关键字段时 Pydantic 拒绝。

当前 Step 2 暂不实现 DAG、调度和真实统计。
