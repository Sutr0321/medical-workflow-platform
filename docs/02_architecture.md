# 02 架构说明

## 1. 总体架构

```text
用户提出研究问题
        ↓
LLM 语义层
        ↓
Candidate Research Spec
        ↓
固定 Validator
        ↓
人工补充 / 审核
        ↓
Frozen Research Spec
        ↓
Rule Engine
        ↓
YAML Template
        ↓
DAG
        ↓
Workflow Engine
        ↓
Algorithm Registry
        ↓
Algorithm Block
        ↓
Result Registry
```

截至 V0.1，已经实现到 Frozen Research Spec，并完成 Algorithm I/O 与 Result Schema Contract。

## 2. 当前模块

### src/medflow/llm

负责自然语言语义提取。

主要文件：

- `client.py`：DeepSeek API Client
- `spec_generator.py`：自然语言 → Candidate Research Spec

约束：

- 只提取明确表达的信息
- 缺失字段保持 null
- 不负责 open issues
- 不负责是否允许冻结
- 不负责统计计算

### src/medflow/contracts

负责平台中的结构化数据格式。

当前包括：

- `candidate_spec.py`
- `reviewed_spec.py`
- `frozen_spec.py`
- `algorithm_io.py`
- `result.py`

### src/medflow/spec

负责 Research Spec 的确定性业务逻辑。

当前包括：

- `candidate_validator.py`
- `candidate_updater.py`
- `readiness.py`
- `review_service.py`
- `freeze_service.py`
- `store.py`

## 3. Research Spec 状态

### NEEDS_INPUT

存在 blocking open issues。

### READY_FOR_REVIEW

所有 blocking issues 已解决，可以交由科研人员人工审核。

### READY_FOR_DATA_BINDING

科研人员已经明确确认。

### FROZEN

生成正式不可变研究方案版本。

## 4. 为什么 open issues 不交给 LLM

如果让 LLM 自己判断“还缺什么”，同一输入可能产生不同问题。

当前做法：

```text
LLM
只生成字段
    ↓
固定 Validator
读取字段
    ↓
固定规则产生 open issues
```

因此同一个 Candidate Spec 可以得到稳定的校验结果。

## 5. Hash

Frozen Research Spec 会生成 content_hash。

相同研究内容应产生相同 hash。

时间戳、人工确认时间等运行信息不应改变研究内容 hash。

主要用途：

- 内容完整性检查
- 方案版本追踪
- 后续结果溯源

## 6. Algorithm Contract

当前 V0.1 以 Logistic Regression 作为第一种算法样板。

Algorithm Input 当前主要描述：

- algorithm_name
- algorithm_version
- dataset_ref
- outcome_column
- exposure_column
- covariate_columns

Algorithm Output 当前主要描述：

- status
- n_used
- term
- effect measure
- estimate
- confidence interval
- p value
- warnings
- error message

当前只是 Contract，真实统计计算尚未接入。

## 7. Result Contract

Result Record 用于后续 Result Registry。

需要能够关联：

```text
Result
  ↓
spec_id + spec_version
  ↓
algorithm_name + algorithm_version
```

确保结果知道自己来自：

- 哪份研究方案
- 哪个方案版本
- 哪个算法
- 哪个算法版本

## 8. 下一阶段设计

下一阶段：

```text
Frozen Spec
   ↓
Rule Engine
   ↓
YAML Template
   ↓
DAG
```

例如：

```text
study_design = cross_sectional
outcome.data_type = binary
analysis.method = logistic_regression
```

固定规则应选择对应的 YAML Template。

该过程不调用 LLM。
