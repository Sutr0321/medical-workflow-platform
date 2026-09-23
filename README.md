# Medical Workflow Platform

医学数据分析工作流平台（Medical Workflow Platform）面向医学科研数据分析场景，目标是把“研究问题 → 研究方案 → 数据绑定 → 工作流 → 统计算法 → 结果”拆成可确认、可追溯、可验证的标准流程。

> 核心边界：LLM 负责自然语言理解和候选方案整理；正式统计执行由固定规则、版本化工作流和已验证算法模块完成。

## 当前架构

```text
研究问题
  ↓
LLM Semantic Extractor
  ↓
Candidate Research Spec
  ↓
Candidate Proposal
  ↓
科研人员人工审核
  ↓
Review Decision Log
  ↓
Frozen Execution Research Spec
  ↓
Data Binding
  ↓
Rule / YAML Template
  ↓
DAG
  ↓
Workflow Engine
  ↓
Algorithm Registry / Algorithm Block
  ↓
Result Registry
  ↓
Golden Test / Publication Output
```

## 当前状态

稳定基线：

```text
v0.1.0-schema-contract
```

当前开发分支：

```text
feat/research-spec-v0.2
```

V0.2 重点解决一个问题：

> 不再把“AI/系统给人看的候选建议”和“真正给机器执行的 Research Spec”混在同一个对象里。

当前已增加：

- Candidate Proposal V0.2
- Proposal Item / Option
- Generic Review Engine
- Review Decision Log
- Research Plan V0.2
- 模糊语义拦截
- Research Plan content hash
- Proposal / Review Log / Research Plan 分离存储
- V0.2 自动验收脚本
- V0.2 交互 Demo

真实 Logistic Regression、Data Binding、Rule Engine、DAG 和 Workflow Engine 仍未实现。

## V0.2 三层分离

### 1. Candidate Proposal

面向科研人员。

可以包含：

- 当前值
- 推荐/说明理由
- 受控候选项
- 自定义输入入口
- blocking 状态
- provenance

它不是 Workflow 输入。

### 2. Review Decision Log

记录：

- 谁审核
- 审核时间
- 哪个字段
- 原始值
- 最终值
- keep / choose / custom / clear

用于审计人工决策。

### 3. Frozen Research Plan

冻结已经人工确认的研究意图和标准化语义：

```text
cross_sectional
association
binary
continuous
logistic_regression
complete_case_global
```

禁止：

- 待确认
- 视情况而定
- 若为横断面
- 可选
- 推荐理由
- 备选方案
- open issues

真实数据列名、实际源单位、编码和派生规则不放在 Research Plan 中，留到后续 Data Binding。Research Plan 本身不能直接执行。

## 运行

Windows：

```bat
python -m venv .venv
.venv\Scripts\activate
pip install pydantic openai python-dotenv
```

配置根目录 `.env`：

```text
DEEPSEEK_API_KEY=你的API_KEY
```

### V0.1 基线测试

```bat
python examples\test_schema_contracts.py
python examples\test_candidate_update.py
```

### V0.2 新增验收

```bat
python examples\test_research_spec_v02.py
```

### V0.2 新交互 Demo

```bat
python examples\run_research_spec_v02_demo.py
```

V0.2 正式冻结后会分开保存：

```text
artifacts/planning_v02/<plan_id>/v1/
├── proposal.json
├── review_log.json
└── research_plan.json
```

其中后续必须先完成 Data Binding；只有 Research Plan + Data Binding 才能生成真正的可执行分析任务。

## 协作

- `main`：稳定版本
- `feat/*`：功能分支
- `fix/*`：修复分支
- Pull Request：Review 后合并
- Issue：记录目标、范围、验收标准

详细见 [CONTRIBUTING.md](CONTRIBUTING.md)。

项目进度见 [docs/03_progress.md](docs/03_progress.md)。

开发路线见 [docs/04_roadmap.md](docs/04_roadmap.md)。
