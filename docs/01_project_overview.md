# 01 项目介绍

## 1. 项目名称

医学数据分析工作流平台（Medical Workflow Platform）

## 2. 为什么做这个项目

医学科研数据分析通常会经历：

```text
提出研究问题
→ 明确研究对象与变量
→ 数据准备
→ 模型分析
→ 统计结果整理
→ 图表与论文结果输出
```

实际科研协作中常见的问题包括：

- 不同研究者使用不同代码结构和命名方式
- 同一种分析需要反复手工搭建
- 自然语言研究问题容易存在遗漏或歧义
- AI 直接生成代码时难以审计和复现
- 算法版本、输入、输出和结果缺乏统一规范
- 后续人员难以判断某个结果由哪份方案、哪版算法产生

本项目的目标不是让大模型直接完成统计，而是把医学数据分析过程拆成标准化模块，并让这些模块通过明确 Contract 连接。

## 3. 核心原则

> **自然语言理解和正式统计计算严格分离。**

LLM 主要负责：

- 理解研究者表达
- 整理结构化研究方案
- 提醒仍需确认的研究决策
- 和研究者进行多轮方案讨论

确定性程序负责：

- Schema 校验
- Readiness
- Freeze
- Workflow
- Algorithm 调用
- Result 保存
- 审计与复现

因此，LLM 不是正式统计计算器，也不是正式结果来源。

## 4. 第一阶段开发主线

当前仍按照最初设计的“最小可运行闭环”推进：

```text
第 1 步  定义 Schema
   ↓
第 2 步  写一个简单 YAML
   ↓
第 3 步  YAML 转成 DAG
   ↓
第 4 步  先用 Mock 算法
   ↓
第 5 步  做简单 Workflow Engine
   ↓
第 6 步  加 Algorithm Registry
   ↓
第 7 步  结果进入 Result Registry
   ↓
第 8 步  替换 1 个真实算法
```

当前：

```text
Step 1 ✅ 完成
Step 2 ⬅️ 下一步
```

## 5. Step 1：Schema Contract 已完成

第一版至少要求三个 Contract：

### Research Spec / Research Plan

规定研究方案必须有哪些字段。

目前已经覆盖：

- 研究设计
- 数据来源和研究周期
- 研究人群
- 暴露
- 结局
- 敏感性结局定义
- 协变量
- 缺失值策略
- 主分析方法
- 效应量
- 置信区间
- 复杂抽样要求
- 次要分析
- 敏感性分析

### Algorithm Input / Output

规定算法模块的统一输入与输出格式。

当前已有：

- `AlgorithmInputV01`
- `AlgorithmEstimateV01`
- `AlgorithmOutputV01`

第一版以 Logistic Regression 为样板，后续再扩展。

### Result

当前已有：

- `ResultRecordV01`

统一描述：

- 算法名称
- 算法版本
- 样本量
- 估计值
- 置信区间
- P 值
- 运行状态
- 时间戳

注意：当前完成的是 Result **Schema**，不是 Result Registry。

## 6. Conversational Research Planning V0.3

在 Step 1 的基础上，项目额外完成了 Research Planning 的产品化入口：

```text
用户自然语言 / 完整研究方案
        ↓
Conversational Planning Agent
        ↓
Structured Research State
        ↓
Deterministic Readiness
        ↓
Research Plan Preview
        ↓
用户确认
        ↓
Frozen Research Plan
```

当前支持：

- 多轮自然语言讨论
- 用户明确决策记录
- AI suggestions 与正式决定分离
- 已确认字段避免重复追问
- 富提示词一次提取
- 不完整方案禁止冻结
- 人工确认后确定性 Freeze
- Plan ID / Version / Content Hash
- transcript / review log / research plan 分离保存

目前已经完成一次 NHANES 横断面研究方案的端到端人工验收。

## 7. Frozen Research Plan 的定位

Frozen Research Plan 可以理解为：

> 科研人员确认后的机器可读研究任务书。

它冻结的是“研究意图”，而不是所有真实数据库细节。

后续真实执行还会需要：

- source file
- source column
- actual unit
- coding
- reference group
- weight / PSU / strata
- derivation rule

这些属于后续 Data Binding / Executable Analysis Spec。

## 8. 当前下一步

当前不继续扩 Research Planning。

下一步严格进入主线 Step 2：

> **只写一个简单的 YAML 流程，并保证程序能正确读取和校验。**

第一版场景：

```text
横断面研究 + 二分类结局
```

流程：

```text
数据准备 → 基线表 → Logistic → RCS
```

此时 YAML 只负责描述流程，不做统计，也不绑定真实 NHANES 变量。

## 9. 最终目标

最终希望形成：

```text
研究问题
→ Research Plan
→ 流程配置
→ DAG
→ Workflow
→ 已验证算法
→ Result Registry
→ 表格 / 图片 / Manifest
```

并能够证明：

> 平台自动分析结果与人工标准分析结果一致。
