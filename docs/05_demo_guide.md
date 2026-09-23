# 05 Demo 演示指南

## 1. 当前 Demo 能展示什么

当前 Demo 主要展示：

```text
用户自然语言课题
        ↓
DeepSeek 提取条件
        ↓
Research Spec
        ↓
固定 Validator
        ↓
人工补充
        ↓
人工审核
        ↓
Frozen Research Spec V1
```

当前 Demo **尚未执行真实统计模型**。

## 2. 演示前准备

Windows 项目目录示例：

```text
G:\code_project\medical-workflow-platform
```

进入项目：

```bat
cd /d G:\code_project\medical-workflow-platform
```

激活环境：

```bat
.venv\Scripts\activate
```

确认根目录存在：

```text
.env
```

但投屏时不要打开 `.env`，避免暴露 API Key。

## 3. 推荐先跑 Schema Contract

```bat
python examples\test_schema_contracts.py
```

重点展示：

```text
PASS：Algorithm Input 合法
PASS：Algorithm Output 合法
PASS：Result Record 合法
PASS：非法字段被 Schema 自动阻止
```

解释：

> 平台先统一规定各模块之间的数据格式，防止每个算法自己定义一套接口。

## 4. Research Spec 自动验收

运行：

```bat
python examples\test_candidate_update.py
```

重点展示：

- NEEDS_INPUT
- READY_FOR_REVIEW
- 人工确认
- FROZEN
- content_hash
- 不完整方案不能确认
- Frozen 对象不能修改
- Frozen V1 不能覆盖

## 5. 交互 Demo

运行：

```bat
python examples\run_research_spec_demo.py
```

### 测试课题 A：信息不完整

输入：

```text
我想研究成年人中 Vitamin D 水平与高血压之间的关系，并调整年龄、性别和 BMI。
```

预期：

- AI 提取 Vitamin D、高血压、年龄、性别、BMI
- 未明确内容保持 null
- Validator 自动提出问题
- 用户补充分析条件
- 用户确认后冻结

如果原问题未明确 Logistic Regression，系统应要求人工确认分析方法。

### 测试课题 B：信息较完整

输入：

```text
基于 NHANES 开展横断面研究，纳入20岁及以上成年人，研究血清尿酸水平与高血压之间的关联。血清尿酸作为连续变量并以连续形式进入模型，高血压作为二分类结局，调整年龄、性别和 BMI，采用多变量 Logistic 回归分析，并采用完整病例分析。
```

预期：

DeepSeek 可以提取：

- cross_sectional
- NHANES
- age_min = 20
- 血清尿酸
- continuous
- 高血压
- binary
- 年龄、性别、BMI
- logistic_regression
- complete_case_global

仍未明确的信息由 Validator 提示人工补充。

## 6. 最后人工确认

系统显示完整 Research Spec 后：

```text
是否确认？ [y/n]
```

### 输入 y

进入：

```text
Reviewed
↓
Frozen V1
```

### 输入 n

应允许：

```text
返回修改
↓
再次审核
↓
再次确认
```

不能自动冻结未经用户确认的方案。

## 7. 最终文件

冻结结果保存在：

```text
artifacts/
└── specs/
    └── RS-XXXXXXXXXXXX/
        └── v1.json
```

可以现场打开该 JSON。

重点说明：

> Frozen Research Spec 是后续 Rule、YAML、DAG 和 Workflow 的唯一正式研究方案输入之一。

## 8. 推荐汇报话术

可以用下面这段作为简短介绍：

> 当前完成的是平台最前端的 Research Spec 和 Schema Contract。用户先用自然语言提出研究问题，DeepSeek 只负责提取明确存在的条件，不允许自行补充统计设计。固定 Validator 再检查缺失信息，由科研人员补充并最终确认。确认后 Research Spec 被正式冻结，生成版本号、ID 和内容 Hash。后续 Workflow 不再依赖大模型自由发挥，而是读取这份冻结研究方案，通过固定规则、YAML、DAG 和经过验证的算法模块执行统计分析。
