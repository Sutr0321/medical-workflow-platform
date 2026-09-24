# 05 Demo 演示指南

## 1. 当前 Demo 能展示什么

当前 Demo 主要展示 Step 1 已完成的两部分：

### Schema Contract

```text
Research Plan Schema
Algorithm Input / Output Schema
Result Schema
Pydantic Validation
```

### Conversational Research Planning V0.3

```text
用户研究方案
→ Conversational Planning
→ Structured Research State
→ Readiness
→ Research Plan Preview
→ 人工确认
→ Frozen Research Plan
```

当前 Demo **不会执行真实统计模型**，也还没有进入 YAML / DAG / Workflow。

## 2. 演示前准备

Windows 项目目录示例：

```text
G:\code_project\medical-workflow-platform
```

进入项目并激活环境：

```bat
cd /d G:\code_project\medical-workflow-platform
.venv\Scripts\activate
```

确认根目录存在 `.env`。

投屏时不要打开 `.env`，避免暴露 API Key。

## 3. Schema Contract 演示

运行：

```bat
python examples\test_schema_contracts.py
```

重点说明：

- Algorithm Input 有统一格式
- Algorithm Output 有统一格式
- Result 有统一格式
- 非法 P 值会被拒绝
- 缺少 outcome column 会被拒绝
- 负数样本量会被拒绝
- 非法 version 会被拒绝

汇报时可以解释：

> 平台第一步先统一规定各模块之间“怎么说话”，避免不同同学开发的算法接口完全不一致。

## 4. Conversational Planning 自动验收

运行：

```bat
python examples\test_conversational_planning_v03.py
```

它主要验证：

- Research Plan readiness
- 已确认字段不会重复成为主动讨论目标
- NHANES 周期缺失时不能冻结
- 冻结命令由系统路由
- 多变量模型但协变量为空时不能冻结
- Rich Research Plan 冻结时不丢字段
- Research Plan 与当前执行能力分离
- Artifact 能被保存
- 不完整方案不能冻结

## 5. Conversational Planning Demo

运行：

```bat
python examples\run_conversational_planning_v03.py
```

首轮支持多行输入。

完整研究方案粘贴结束后，单独输入：

```text
/send
```

提交首轮内容。

进入正常会话后：

> 每条回复直接按回车提交，不再需要 `/send`。

可随时输入：

```text
预览方案
冻结方案
退出
```

## 6. 推荐演示场景

可以使用：

```text
横断面研究
+
NHANES
+
20岁及以上成年人
+
连续暴露
+
二分类结局
+
复杂抽样 Logistic
+
敏感性分析
```

如果没有提供 NHANES 调查周期，系统应保持：

```text
DISCUSSING
```

并要求补充调查周期。

补充周期后，若其他 blocking decisions 已完整：

```text
READY_TO_FREEZE
```

## 7. Preview 与 Freeze

输入：

```text
预览方案
```

查看 Research Plan。

输入：

```text
冻结方案
```

系统再次显示方案并要求人工确认。

用户确认后生成：

```text
Frozen Research Plan
Plan ID
Version
Content Hash
```

## 8. 冻结文件

保存在：

```text
artifacts/
└── conversations_v03/
    └── <plan_id>/
        └── v1/
            ├── planning_session.json
            ├── transcript.json
            ├── review_log.json
            └── research_plan.json
```

打开 JSON 时 Windows PowerShell 建议显式使用 UTF-8：

```powershell
Get-Content "path\to\research_plan.json" -Encoding UTF8 -Raw
```

## 9. 当前 Demo 的边界

当前已经完成的是：

```text
Step 1 Schema Contract
+
Conversational Research Planning V0.3
```

当前尚未实现：

- Simple YAML
- DAG
- Mock Workflow
- Workflow Engine
- Algorithm Registry
- Result Registry
- Data Binding
- Executable Analysis Spec
- 真实 Logistic
- Golden Test

## 10. 下一次开发从哪里开始

下一步严格从：

> **Step 2：Simple YAML**

开始。

第一版只做：

```text
横断面 + 二分类
数据准备 → 基线表 → Logistic → RCS
```

目标只要求程序能够正确读取和校验 YAML。

暂时不做 DAG，不调用算法，也不运行真实统计。
