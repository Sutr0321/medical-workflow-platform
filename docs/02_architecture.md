# 02 架构说明

## 1. 目标运行架构

最终平台希望形成：

```text
用户研究问题
        ↓
Conversational Research Planning
        ↓
Frozen Research Plan
        ↓
Data Binding
        ↓
Executable Analysis Spec
        ↓
Rule / YAML
        ↓
DAG
        ↓
Workflow Engine
        ↓
Algorithm Registry / Block
        ↓
Result Registry
        ↓
Tables / Figures / Manifest
```

这描述的是最终运行时各层之间的关系。

## 2. 当前开发主线

第一阶段不按“最终架构一次全部实现”，而是按照最小可运行闭环逐步验证：

```text
Step 1  Schema Contract            ✅
Step 2  Simple YAML                ⬅️ NEXT
Step 3  YAML → DAG                 ⬜
Step 4  Mock Algorithm             ⬜
Step 5  Workflow Engine            ⬜
Step 6  Algorithm Registry         ⬜
Step 7  Result Registry            ⬜
Step 8  Replace One Real Algorithm ⬜
```

Data Binding / Executable Analysis Spec 仍属于最终架构的重要层，但不作为当前 Step 2 的前置任务。

第一版 YAML 可以只使用逻辑任务名和算法名，真实数据字段后续再绑定。

## 3. Research Planning 层

用户主要看到自然语言对话，而不是 JSON 或 field_path。

后台每个 `PlanningSessionV03` 保存：

- session_id
- messages
- current_candidate
- confirmed_fields
- decisions
- pending_suggestions
- status
- created_at / updated_at

状态：

```text
DISCUSSING
READY_TO_FREEZE
FROZEN
```

## 4. 两阶段对话处理

每轮对话：

```text
用户消息
→ interpret_updates
→ 确定性更新 Research State
→ 重新计算 discussion_targets
→ compose_reply
```

只有用户当前消息已经明确表达的内容才能成为正式 update。

AI 自己提出的候选方案只能成为 suggestion；未被用户确认前不能写入正式研究状态。

## 5. 确定性边界

V0.3 中固定程序负责：

- Schema 校验
- 允许更新的 field_path
- Pydantic 类型约束
- readiness
- freeze 前完整性检查
- content hash
- immutable Frozen Research Plan
- 系统命令路由
- 必要的确定性文本规范化

另外：

- Research Plan 与当前执行能力分离
- 未核验的数据库事实不能由 Planning Agent 直接当作正式事实
- Data Binding 之前不确认真实列名、真实单位、权重、PSU、strata 等

## 6. Preview 与 Freeze

`ResearchPlanPreviewV03` 从同一结构化状态生成可读预览。

Freeze 不调用 LLM。

只有：

```text
READY_TO_FREEZE
+
用户最终确认
```

才生成：

```text
FrozenResearchPlanV03
```

冻结后当前版本不允许直接修改。

## 7. Frozen Artifact

当前冻结后保存：

```text
artifacts/conversations_v03/<plan_id>/v1/
├── planning_session.json
├── transcript.json
├── review_log.json
└── research_plan.json
```

## 8. Step 2 的架构边界

下一步只实现：

```text
Simple YAML
+
YAML Reader
+
YAML Schema Validation
```

YAML 第一版只描述：

- step id
- depends_on
- algorithm id
- algorithm version

例如逻辑上：

```text
data_prepare
→ baseline_table
→ logistic
→ rcs
```

Step 2 **不负责**：

- 建 DAG
- 拓扑排序
- 检测循环依赖
- 调度算法
- 找 Registry
- 保存 Result
- 绑定真实 NHANES 字段
- 执行真实统计

这些属于后续步骤。

## 9. Data Binding 边界

后续进入真实数据执行前，Data Binding 负责：

- source file
- source variable
- actual source unit
- coding
- reference group
- transformation
- derived variable
- derivation rule
- survey weight / strata / PSU

因此：

> Research Plan 回答“要研究什么”；YAML 回答“流程有哪些步骤”；Data Binding 回答“真实数据库里用什么表示”；Executable Analysis Spec 回答“机器具体怎么执行”。
