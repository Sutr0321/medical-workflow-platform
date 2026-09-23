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

在实际科研协作中，经常会出现以下问题：

- 不同研究者使用不同代码结构和命名方式
- 同一种分析需要反复手工搭建
- 自然语言研究问题容易存在遗漏或歧义
- AI 直接生成代码时，结果难以审计和复现
- 算法版本、输入、输出和结果缺乏统一规范
- 后续人员难以判断某个结果究竟由哪份方案、哪版算法产生

本项目尝试把医学数据分析过程拆成标准化模块。

## 3. 核心思想

项目最重要的原则是：

> **把“自然语言理解”和“统计计算”严格分离。**

LLM 主要处理：

```text
研究人员自然语言
        ↓
结构化 Research Spec
```

真正的统计执行由后续固定系统完成：

```text
Frozen Research Spec
        ↓
Rule / YAML
        ↓
DAG
        ↓
Workflow Engine
        ↓
注册算法
        ↓
Result Registry
```

因此，LLM 不是统计计算器，也不是正式结果来源。

## 4. Research Spec 是什么

Research Spec 可以理解成：

> 一份机器可读、科研人员确认后的“分析任务书”。

当前字段主要包括：

- 研究设计
- 数据来源
- 研究人群
- 暴露变量
- 结局变量
- 协变量
- 缺失值处理策略
- 主分析方法
- 待确认问题

当前 Research Spec 生命周期：

```text
Candidate
    ↓
Reviewed
    ↓
Frozen
```

### Candidate

由 DeepSeek 从研究问题中提取明确存在的信息。

### Reviewed

固定 Validator 检查后，科研人员补齐必要条件并人工确认。

### Frozen

人工确认后生成不可变版本，并记录：

- spec_id
- spec_version
- content_hash
- frozen_at

后续流程应只读取 Frozen Research Spec。

## 5. 为什么需要 Frozen

冻结后不能偷偷改变研究方案。

例如：

```text
RS-XXXX
V1
Hash: abc...
```

后续产生的 Workflow 和 Result 都可以追溯到这一个明确版本。

如果以后研究方案发生变化，应形成新的版本，而不是修改旧结果对应的历史方案。

## 6. Schema Contract

当前第一阶段已经完成三类基础 Contract：

### Research Spec Schema

规定研究方案字段和数据类型。

### Algorithm Input / Output Schema

规定算法模块必须接收什么、返回什么。

### Result Schema

规定正式统计结果如何统一保存。

这样后续多个模块之间通过结构化数据通信，而不是相互依赖内部代码。

## 7. 当前 V0.1 支持范围

当前主要完成平台框架的第一段。

支持：

- DeepSeek 语义提取
- Research Spec
- 人工确认与冻结
- Algorithm I/O Contract
- Result Contract

当前只将：

```text
logistic_regression
```

作为第一个统计方法样板。

这并不意味着最终平台只支持 Logistic Regression。

未来目标是通过 Algorithm Registry 扩展：

- Logistic Regression
- Linear Regression
- Cox Regression
- RCS
- Survey-weighted Regression
- Mediation
- Clustering
- 其他经过验证的算法模块

## 8. 最终目标

最终希望形成：

```text
研究问题
→ Research Spec
→ 人工确认
→ 自动工作流
→ 标准算法
→ 标准结果
→ 可追溯分析记录
```

并能够证明：

> 平台自动分析结果与人工标准分析结果一致。
