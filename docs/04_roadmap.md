# 04 开发路线图

## 目标

先完成一个真正可运行、可验证的小闭环，再扩展更多算法和数据库。

最终 Demo：

```text
研究问题
↓
Research Spec
↓
人工确认冻结
↓
Rule Engine
↓
YAML
↓
DAG
↓
Workflow
↓
真实算法
↓
Result Registry
↓
与人工结果一致
```

## Phase 1：Schema Contract

状态：✅ 已完成 V0.1

内容：

- Research Spec Schema
- Algorithm Input Schema
- Algorithm Output Schema
- Result Schema
- Pydantic 校验
- Research Spec 冻结

版本标签：

```text
v0.1.0-schema-contract
```

## Phase 2：Rule + YAML Template

状态：⏳ 下一阶段

目标：

输入 Frozen Research Spec 后，由固定规则选择 YAML Template。

第一版只支持：

```text
cross_sectional
binary outcome
logistic_regression
```

计划文件：

```text
src/medflow/rules/
config/templates/
```

验收：

- 相同 Spec 选择相同 Template
- 不调用 LLM
- 不支持组合 Fail Closed

## Phase 3：YAML → DAG

状态：⬜

目标：

将 YAML Workflow 转换为 DAG。

需要：

- Node Schema
- Edge Schema
- DAG Parser
- DAG Validator
- 环检测
- 拓扑排序

验收：

- 合法 DAG 正确生成
- 循环依赖被阻止
- 缺失节点被阻止

## Phase 4：Algorithm Registry + Mock Block

状态：⬜

目标：

建立算法注册机制。

第一版：

```text
logistic_regression
```

先接 Mock Block，不进行真实统计。

验收：

- Workflow 只通过 Registry 找算法
- 算法不存在则 Fail Closed
- 算法版本可记录

## Phase 5：Workflow Engine

状态：⬜

目标：

按照 DAG 顺序执行节点。

第一版只做：

- 单机
- 串行
- 明确状态
- 错误即停止

状态建议：

```text
PENDING
RUNNING
SUCCESS
FAILED
```

## Phase 6：Result Registry

状态：⬜

目标：

把 Algorithm Output 保存成标准 Result Record。

需要记录：

- result_id
- spec_id
- spec_version
- algorithm_name
- algorithm_version
- n_used
- estimate
- CI
- P
- timestamp

## Phase 7：真实 Logistic Regression Block

状态：⬜

目标：

用真实数据执行第一种统计模型。

第一版只解决：

```text
连续/分类暴露
+
二分类结局
+
协变量调整
```

真实统计实现应与人工标准代码进行对比。

## Phase 8：Golden Test

状态：⬜

目标：

证明自动工作流与人工标准统计分析一致。

需要固定：

- 测试数据
- Research Spec
- 人工标准结果
- 自动结果
- 容差规则

达到一致后，才将算法 Block 标记为验证通过。

## Phase 9：扩展算法

状态：⬜

在第一个闭环稳定后再增加：

- Linear Regression
- Cox Regression
- RCS
- Survey-weighted Regression
- Kaplan-Meier
- Mediation
- Clustering

原则：

> 新增算法尽量通过注册扩展，而不是修改 Workflow Engine 核心代码。

## Phase 10：Web Demo

状态：⬜

在后端闭环稳定后，再实现：

- 研究问题输入
- Research Spec 表单
- open issues 交互
- 人工确认
- Workflow 状态展示
- Result 展示

不在当前阶段提前开发复杂前端。
