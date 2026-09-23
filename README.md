# Medical Workflow Platform

医学数据分析工作流平台（Medical Workflow Platform）是一个面向医学科研数据分析场景的工作流平台原型。

当前项目的核心目标不是“让大模型直接做统计”，而是把医学研究分析拆成一套可确认、可复现、可审计、可维护的标准流程：

```text
研究问题
  ↓
LLM 整理研究条件
  ↓
Research Spec
  ↓
科研人员人工确认并冻结
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
标准化统计结果
```

> 核心边界：LLM 负责自然语言理解和候选研究方案整理；统计计算最终由固定、注册、版本化、可验证的算法模块完成。

## 当前状态

当前版本处于 **V0.1：Schema Contract 完成，准备进入 Rule + YAML Template 阶段**。

已完成：

- DeepSeek API 接入
- 自然语言研究问题 → Candidate Research Spec
- Pydantic Research Spec Schema
- 固定 Validator 与 open issues
- 用户补充研究条件
- Research Spec readiness 判断
- 人工确认
- Frozen Research Spec
- spec_id / spec_version / content_hash
- Frozen JSON 快照保存
- Frozen 对象禁止直接修改
- 已有 Frozen V1 禁止覆盖
- Algorithm Input Schema
- Algorithm Output Schema
- Result Schema
- Schema Contract 测试
- Research Spec 命令行交互 Demo

当前 V0.1 只以 **Logistic Regression** 作为第一个标准算法样板；真实 Logistic 统计执行尚未接入。

详细进度见 [docs/03_progress.md](docs/03_progress.md)。

## 项目目录

```text
medical-workflow-platform/
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── docs/
│   ├── 01_project_overview.md
│   ├── 02_architecture.md
│   ├── 03_progress.md
│   ├── 04_roadmap.md
│   └── 05_demo_guide.md
├── examples/
│   ├── run_research_spec_demo.py
│   ├── test_candidate_update.py
│   ├── test_deepseek.py
│   ├── test_schema_contracts.py
│   └── test_spec_generator.py
├── src/
│   └── medflow/
│       ├── contracts/
│       ├── llm/
│       └── spec/
└── artifacts/
    └── specs/
```

## 当前架构边界

### LLM 可以做

- 理解用户自然语言研究问题
- 提取用户明确给出的研究条件
- 形成 Candidate Research Spec

### LLM 不可以做

- 自行补充用户没有说明的科研条件
- 自行选择统计方法
- 自行决定是否可以冻结 Research Spec
- 直接决定统计计算流程
- 直接作为正式统计结果来源

例如，当用户没有明确说明分析方法时：

```json
{
  "analysis": {
    "method": null
  }
}
```

由固定 Validator 检测缺失，再由科研人员确认。

## Research Spec 当前流程

```text
自然语言问题
    ↓
ResearchSpecGenerator
    ↓
CandidateResearchSpecV01
    ↓
CandidateSpecValidator
    ↓
NEEDS_INPUT / READY_FOR_REVIEW
    ↓
CandidateSpecUpdater
    ↓
科研人员确认
    ↓
ReviewedResearchSpecV01
    ↓
SpecFreezeService
    ↓
FrozenResearchSpecV01
    ↓
artifacts/specs/<spec_id>/v1.json
```

## 快速运行

### 1. 创建虚拟环境

Windows：

```bat
python -m venv .venv
.venv\Scripts\activate
```

### 2. 安装当前依赖

当前项目尚未固定 requirements.txt，可先安装：

```bat
pip install pydantic openai python-dotenv
```

### 3. 配置 DeepSeek API Key

在项目根目录创建：

```text
.env
```

填写：

```text
DEEPSEEK_API_KEY=你的API_KEY
```

注意：`.env` 已加入 `.gitignore`，禁止提交 API Key。

### 4. Schema Contract 验收

```bat
python examples\test_schema_contracts.py
```

### 5. Research Spec 自动验收

```bat
python examples\test_candidate_update.py
```

### 6. 运行交互 Demo

```bat
python examples\run_research_spec_demo.py
```

详细演示步骤见 [docs/05_demo_guide.md](docs/05_demo_guide.md)。

## 当前稳定版本

当前阶段标签：

```text
v0.1.0-schema-contract
```

对应含义：

> Research Spec 核心闭环和第一版 Schema Contract 已完成并通过本地验收。

## 下一阶段

下一阶段重点：

```text
Frozen Research Spec
        ↓
固定 Rule
        ↓
YAML Template
        ↓
YAML → DAG
```

详细路线见 [docs/04_roadmap.md](docs/04_roadmap.md)。

## 协作

项目采用：

- `main`：稳定可运行版本
- `feat/*`：新功能分支
- `fix/*`：问题修复分支
- Pull Request：合并到 main 前进行检查
- Issue：记录任务、问题和验收标准

详细规则见 [CONTRIBUTING.md](CONTRIBUTING.md)。
