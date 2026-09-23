# 03 项目进度

最后更新：2026-09-23

## 1. 稳定基线

```text
v0.1.0-schema-contract
```

V0.1 已完成并保留，不直接重写历史版本。

## 2. 当前开发

当前分支：

```text
feat/research-spec-v0.2
```

当前目标：

> **Research Planning / Review Layer V0.2**

## 3. 已完成

| 模块 | 状态 | 说明 |
|---|---|---|
| DeepSeek API | ✅ | 已接入 |
| Candidate Research Spec V0.1 | ✅ | 稳定基线 |
| 固定 Validator / open issues | ✅ | 不依赖 LLM |
| Candidate Updater | ✅ | 支持结构化人工补充 |
| Freeze / Hash / Store V0.1 | ✅ | 已测试 |
| Algorithm I/O Schema | ✅ | 已测试 |
| Result Schema | ✅ | 已测试 |
| Candidate Proposal V0.2 | ✅ | 新增人类审核层 |
| Proposal Option / Item | ✅ | 机器值与人类标签分离 |
| Generic Review Engine V0.2 | ✅ | 不按字段复制确认函数 |
| Review Decision Log V0.2 | ✅ | 独立审计记录 |
| Execution Research Spec V0.2 | ✅ | 执行语义与建议层分离 |
| 模糊语义 Fail Closed | ✅ | 执行层阻止待确认/视情况等 |
| Execution Hash / Freeze V0.2 | ✅ | 已实现 |
| Planning Bundle Store | ✅ | 三份 artifact 分离保存 |
| V0.2 自动验收脚本 | ✅ | 已写入分支 |
| V0.2 交互 Demo | ✅ | 已写入分支 |

## 4. 待本地验收

需要在本地执行：

```bat
python examples\test_research_spec_v02.py
```

通过后再执行：

```bat
python examples\run_research_spec_v02_demo.py
```

当前 GitHub 分支已写入代码，但在合并 main 前应完成本地测试。

## 5. 尚未完成

| 模块 | 状态 |
|---|---|
| Data Binding Contract | ⬜ |
| Rule Engine | ⬜ |
| YAML Template | ⬜ |
| YAML → DAG | ⬜ |
| DAG Validator | ⬜ |
| Algorithm Registry | ⬜ |
| Mock Algorithm Block | ⬜ |
| Workflow Engine | ⬜ |
| Result Registry | ⬜ |
| 真实 Logistic Regression Block | ⬜ |
| Golden Test | ⬜ |
| Web 前端 | ⬜ |

## 6. 当前判断

项目目前已经不再只是：

```text
输入一句话
→ 打印 JSON
→ 保存 JSON
```

V0.2 开始形成：

```text
语义提取
→ 候选方案
→ 人工审核
→ 审计日志
→ 明确执行方案
```

但真正跨出 Demo/MVP 的关键节点仍然是：

```text
真实数据绑定
→ 自动 Workflow
→ 真实 Logistic
→ Result Registry
→ 与人工结果一致
```

因此 V0.2 完成后不继续堆 CLI 功能，而应尽快进入执行链。
