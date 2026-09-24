# Medical Workflow Platform

医学数据分析工作流平台（Medical Workflow Platform）面向医学科研数据分析场景。

项目目标不是让大模型直接做统计，而是把研究方案、流程编排、算法执行和结果保存拆成可确认、可追溯、可复现的模块。

## 当前状态

当前已完成第一阶段主线中的 **第 1 步：Schema Contract**，并在此基础上额外完成了 **Conversational Research Planning V0.3**。

当前停止点：

```text
第 1 步  Schema Contract                    ✅ 已完成
         └─ Conversational Planning V0.3    ✅ 已完成主链路验收

第 2 步  简单 YAML 流程                    ⬅️ 下一步
第 3 步  YAML → DAG                        ⬜
第 4 步  Mock 算法                         ⬜
第 5 步  Workflow Engine                   ⬜
第 6 步  Algorithm Registry                ⬜
第 7 步  Result Registry                   ⬜
第 8 步  替换 1 个真实算法                 ⬜
```

当前不继续扩展聊天 Demo，也暂不进入 DAG、Workflow 或真实统计。

## 第一阶段开发主线

按照最小可运行闭环推进：

```text
1. 定义 Schema
   ↓
2. 写一个简单 YAML
   ↓
3. YAML 转成 DAG
   ↓
4. 先用 Mock 算法
   ↓
5. 做最简单 Workflow Engine
   ↓
6. 加简单 Algorithm Registry
   ↓
7. 结果统一进入 Result Registry
   ↓
8. 最后替换 1 个真实算法
```

第一阶段的目标不是一次性完成完整平台，而是验证：

- 研究方案能否被规范表达
- 流程配置能否被读取
- 任务依赖能否被正确组织
- Workflow 能否正确调度算法
- 结果能否统一保存
- 替换真实算法时 Workflow 核心代码是否无需修改

## Step 1：已完成的 Contract

### Research Plan / Research Spec

当前已经能够把研究方案表示为结构化对象，并支持：

- 研究设计
- 数据来源与研究周期
- 研究人群
- 暴露
- 结局及敏感性定义
- 协变量
- 缺失值策略
- 主分析方法
- 效应量
- 置信区间
- 复杂抽样要求
- 次要分析
- 敏感性分析

并支持：

```text
自然语言 / 完整研究方案
→ Conversational Planning
→ Structured Research State
→ Deterministic Readiness
→ Research Plan Preview
→ 人工确认
→ Frozen Research Plan
```

### Algorithm Input / Output

已经定义第一版统一算法接口：

- `AlgorithmInputV01`
- `AlgorithmEstimateV01`
- `AlgorithmOutputV01`

当前 V0.1 以 Logistic Regression 作为接口样板，后续会扩展成更通用的 Algorithm Contract。

### Result Schema

已经定义：

- `ResultRecordV01`

用于规定算法名称、版本、样本量、估计值、置信区间和 P 值等统计结果如何保存。

注意：

- Result **Schema 已完成**
- Result **Registry 尚未实现**

## Conversational Research Planning V0.3

V0.3 允许用户像正常聊天一样讨论研究方案。

后台维护：

- Planning Session
- 对话记录
- 当前 Candidate Research Spec
- 已确认决策
- Pending Suggestions
- Readiness
- Research Plan Preview

关键原则：

- AI 负责理解和对话，不负责正式统计
- AI 建议不能自动成为用户决定
- 已确认字段不会被无意义重复追问
- Freeze 由确定性代码执行
- 不完整方案不能冻结
- Frozen Research Plan 带版本和 Content Hash
- 未经 Evidence / Data Binding 核对，AI 不得把数据库具体变量、权重或文件信息当成已验证事实

当前已经用一个 NHANES 横断面课题完成从富提示词到 Frozen Rich Research Plan 的端到端人工验收。

## 目标运行架构

最终运行链路仍然会逐步扩展到：

```text
Research Question
→ Research Planning
→ Frozen Research Plan
→ Data Binding
→ Executable Analysis Spec
→ Rule / YAML
→ DAG
→ Workflow Engine
→ Algorithm Registry / Block
→ Result Registry
→ Tables / Figures / Manifest
```

这里要区分 **目标运行架构** 和 **当前开发顺序**：

- Data Binding 是最终真实执行所必需的层
- 但当前第一阶段按照最小闭环主线，下一步先做简单 YAML
- 第 2 步 YAML 只使用逻辑任务名，不绑定真实 NHANES 列名
- 真实变量、单位、权重、PSU、strata 等在后续 Data Binding 阶段处理

## 下一步：Step 2 Simple YAML

下一步只做一件事：

> 定义并正确读取一个最简单的 YAML Workflow。

第一条场景固定为：

```text
横断面研究 + 二分类结局
```

流程先写成：

```text
数据准备
→ 基线表
→ Logistic
→ RCS
```

YAML 第一版只描述：

- task / step id
- depends_on
- algorithm id
- algorithm version

验收标准：

- 程序能够正确读取 YAML
- Pydantic 能校验基本字段
- 缺少 step id / algorithm / version 时拒绝
- `depends_on` 能正确读取

**Step 2 暂时不做：**

- DAG
- 拓扑排序
- 环检测
- Workflow 调度
- Algorithm Registry
- Result Registry
- 真实 NHANES 数据绑定
- 真实统计运行

这些分别属于后续步骤。

## 当前主要命令

### Schema Contract

```bat
python examples\test_schema_contracts.py
```

### Conversational Planning 验收

```bat
python examples\test_conversational_planning_v03.py
```

### Conversational Planning Demo

```bat
python examples\run_conversational_planning_v03.py
```

首轮支持多行输入，使用 `/send` 提交；进入正常对话后直接回车提交，不需要再次输入 `/send`。

## 当前稳定基线

```text
v0.1.0-schema-contract
```

当前开发分支：

```text
feat/conversational-planning-v0.3
```
