# Medical Workflow Platform

医学数据分析工作流平台（Medical Workflow Platform）面向医学科研数据分析场景。

项目目标不是让大模型直接做统计，而是把：

```text
研究主题
→ 对话式方案规划
→ 冻结 Research Plan
→ Data Binding
→ Executable Analysis Spec
→ Workflow
→ 已验证算法
→ Result Registry
```

做成可确认、可追溯、可复现的标准流程。

## 当前产品形态

V0.3 开始，Research Planning 不再采用“AI 抽字段 + 用户填表”的主交互方式。

用户只需要先给一个课题主题，然后像正常聊天一样和 AI 讨论：

```text
用户：我想研究维生素D与高血压的关系

AI：可以。我们先把数据来源和研究设计讨论清楚……
    你计划使用什么数据库？

用户：NHANES 2017-2018，20岁以上成年人。

AI：好的，目前已经明确……
    接下来需要讨论结局定义……
```

后台同时维护结构化 Research State。

用户可以随时：

```text
预览方案
冻结方案
退出
```

## 当前架构

```text
课题主题
  ↓
Conversational Planning Agent
  ↓
Planning Session
  ├── conversation messages
  ├── current Candidate Research Spec
  ├── confirmed decisions
  ├── pending AI suggestions
  └── unresolved fields
  ↓
Research Plan Preview
  ↓
用户确认冻结
  ↓
Frozen Research Plan
  ↓
Data Binding
  ↓
Executable Analysis Spec
  ↓
Rule / YAML / DAG / Workflow
  ↓
Algorithm Registry
  ↓
Result Registry
  ↓
Golden Test
```

## AI 的职责

AI 可以：

- 理解研究主题和上下文
- 和科研人员自然对话
- 解释为什么某个问题需要确认
- 提出有限候选方案和理由
- 从用户当前消息中提取明确决定
- 一次推进 1–2 个真正重要的问题

AI 不可以：

- 把自己的建议偷偷写成“已确认”
- 因为结局是 binary 就自动确认 Logistic
- 因为用户说“成年人”就自动设 age_min=18
- 自行确定疾病临床阈值
- 声称已核实真实数据列名、实际单位或编码
- 直接进行正式统计计算

真实 source column、source unit、coding、reference group 和 derivation rule 属于后续 Data Binding。

## V0.3 新增

- `PlanningSessionV03`
- 对话消息历史
- 用户明确决策记录
- AI pending suggestions
- `ConversationalPlanningAgentV03`
- `PlanningSessionServiceV03`
- 确定性 readiness checker
- 人类可读 Research Plan Preview
- 对话完成后的确定性冻结
- conversation transcript / review log / research plan 分离存储
- CLI 对话式 Demo
- V0.3 自动验收脚本

## 运行

先切到 V0.3 分支：

```bat
git fetch origin
git checkout -b feat/conversational-planning-v0.3 origin/feat/conversational-planning-v0.3
```

如果本地已经存在该分支：

```bat
git checkout feat/conversational-planning-v0.3
git pull origin feat/conversational-planning-v0.3
```

### 自动验收

```bat
python examples\test_conversational_planning_v03.py
```

这个测试不调用 DeepSeek。

### 对话式 Demo

```bat
python examples\run_conversational_planning_v03.py
```

运行后直接像聊天一样输入即可。

## 冻结后的产物

```text
artifacts/conversations_v03/<plan_id>/v1/
├── planning_session.json
├── transcript.json
├── review_log.json
└── research_plan.json
```

Research Plan 仍然不是最终可执行统计任务。

下一阶段：

```text
Frozen Research Plan
→ Data Binding
→ Executable Analysis Spec
```

## 当前稳定基线

```text
v0.1.0-schema-contract
```

V0.2 提供 Proposal / Review / Research Plan 分层；
V0.3 在此基础上加入自然语言多轮对话入口。
