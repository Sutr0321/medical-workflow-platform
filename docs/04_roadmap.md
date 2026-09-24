# 04 开发路线图

## 总原则

第一阶段只做最小可运行闭环。

不一次性同时开发真实数据库、真实算法、工作流、前端和报告系统，而是逐层验证接口是否正确。

---

## Step 1：定义 Schema

状态：✅ 已完成

第一版 Contract：

- Research Spec / Research Plan
- Algorithm Input / Output
- Algorithm Estimate
- Result Schema
- Pydantic 校验

在此基础上额外完成：

### Conversational Research Planning V0.3

状态：✅ 主链路人工验收通过

```text
研究主题 / 完整研究方案
→ Conversational Planning
→ Structured Research State
→ Readiness
→ Preview
→ 用户确认
→ Frozen Research Plan
```

这属于 Step 1 的增强，不改变后续主线顺序。

---

## Step 2：只写一个简单 YAML

状态：⬅️ NEXT

第一版场景：

```text
横断面研究 + 二分类结局
```

流程：

```text
数据准备
→ 基线表
→ Logistic
→ RCS
```

YAML 只描述：

- step id
- depends_on
- algorithm id
- algorithm version

第一版验收只要求：

- 能正确读取 YAML
- 能通过 Pydantic 校验
- 缺关键字段时拒绝

这一阶段不执行统计。

---

## Step 3：YAML 转成 DAG

状态：⬜

读取 YAML 后：

- 每个 step 变成一个节点
- `depends_on` 变成边
- 建立合法执行顺序
- 检测循环依赖

验收：

- 能建立节点和边
- 能拓扑排序
- A → B → A 之类循环必须报错

---

## Step 4：算法先用 Mock

状态：⬜

先实现假的算法模块，不做真实统计。

例如 Mock Logistic 可以返回固定结果：

```text
OR = 0.82
P = 0.001
```

目标是验证平台能否：

- 找到算法
- 传入统一输入
- 接收统一输出
- 把结果交给后续模块

---

## Step 5：最简单 Workflow Engine

状态：⬜

第一版只做单机串行。

负责：

- 读取 DAG
- 找当前可运行节点
- 调用算法
- 更新状态
- 失败后阻断不应继续执行的下游节点

第一版状态可包括：

```text
PENDING
RUNNING
SUCCESS
FAILED
```

---

## Step 6：Algorithm Registry

状态：⬜

第一版可以先使用 Python 字典：

```text
algorithm_id + version
→ execution entry
```

后续再扩展运行环境、输入输出 Schema、验证状态等元数据。

---

## Step 7：Result Registry

状态：⬜

注意：

```text
Result Schema    ✅ 已完成
Result Registry  ⬜ 尚未实现
```

第一版 Result Registry 可以先保存 JSON。

核心要求：

- 每次运行有 run_id
- 能找到每个 step 的结果
- 表格和图片以后只读取 Registry，不重新跑模型

---

## Step 8：替换一个真实算法

状态：⬜

当：

```text
方案
→ YAML
→ DAG
→ Workflow
→ Mock
→ Result Registry
```

整条链稳定以后，再替换一个真实算法。

优先候选：

- Baseline Table
- Logistic Regression

成功标准：

> 替换真实算法时，Workflow 核心代码不需要修改，只需要调整 Registry 中的算法入口。

---

# 后续工程扩展

以下模块仍然重要，但不打乱当前 8 步最小闭环主线。

## Data Binding

真实数据执行前需要把 Research Plan 中的研究概念映射到：

- source file
- source variable
- actual unit
- coding
- reference group
- weight / PSU / strata
- derivation rule

## Executable Analysis Spec

输入：

```text
Frozen Research Plan
+
Validated Data Binding
```

输出机器可执行分析任务。

## Golden Test

真实算法接入后，需要证明：

> 平台结果与人工标准代码在预设容差内一致。

## Web UI

后端主链稳定后再开发：

```text
左侧 AI 对话
右侧 Research Plan Preview
底部人工确认 / Freeze
```

---

## 当前唯一下一任务

> **Step 2：Simple YAML。**

在 Step 2 验收完成前，不提前进入 DAG、Workflow、Registry 或真实统计。
