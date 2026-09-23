# 03 项目进度

最后更新：2026-09-23

当前稳定标签：

```text
v0.1.0-schema-contract
```

## 1. 总体状态

当前阶段：

> **Phase 1：Schema Contract V0.1 已完成。**

当前准备进入：

> **Phase 2：Rule Engine + YAML Template。**

## 2. 已完成

| 模块 | 状态 | 说明 |
|---|---|---|
| GitHub 私有仓库 | ✅ | 已建立版本管理 |
| DeepSeek API 接入 | ✅ | 已完成连通测试 |
| 自然语言 → Candidate Research Spec | ✅ | 已运行 |
| Research Spec Pydantic Schema | ✅ | V0.1 |
| Candidate Validator | ✅ | 固定规则 |
| open issues | ✅ | 由程序生成 |
| Candidate 更新 | ✅ | 支持人工补充 |
| Readiness | ✅ | NEEDS_INPUT / READY_FOR_REVIEW |
| 人工确认 | ✅ | 未确认不能冻结 |
| Frozen Research Spec | ✅ | 已运行 |
| spec_id | ✅ | 已生成 |
| spec_version | ✅ | V1 |
| content_hash | ✅ | 已验证稳定性 |
| Frozen 对象防修改 | ✅ | 已测试 |
| Frozen V1 防覆盖 | ✅ | 已测试 |
| Frozen JSON 保存 | ✅ | artifacts/specs |
| analysis.method | ✅ | 当前支持 logistic_regression |
| Algorithm Input Schema | ✅ | 已测试 |
| Algorithm Output Schema | ✅ | 已测试 |
| Result Schema | ✅ | 已测试 |
| Research Spec 命令行 Demo | ✅ | 已可交互运行 |

## 3. 当前 V0.1 验收结果

已验证：

```text
不完整 Research Spec
→ 禁止确认
```

已验证：

```text
人工确认
→ 才允许冻结
```

已验证：

```text
相同研究内容
→ 相同 content_hash
```

已验证：

```text
Frozen Spec
→ 禁止直接修改
```

已验证：

```text
已有 V1 JSON
→ 禁止覆盖
```

已验证 Algorithm / Result Contract 的基础字段类型约束。

## 4. 尚未完成

| 模块 | 状态 |
|---|---|
| Rule Engine | ⬜ |
| YAML Template | ⬜ |
| YAML → DAG | ⬜ |
| DAG Validator | ⬜ |
| Algorithm Registry | ⬜ |
| Mock Algorithm Block | ⬜ |
| Workflow Engine | ⬜ |
| Result Registry | ⬜ |
| 真实 Logistic Regression Block | ⬜ |
| 数据绑定层 | ⬜ |
| Golden Test | ⬜ |
| Web 前端 | ⬜ |

## 5. 当前限制

当前版本只将 Logistic Regression 作为第一个标准算法样板。

这不是最终算法范围。

当前尚不能：

- 自动执行真实 Logistic Regression
- 自动构建 DAG
- 自动运行完整 Workflow
- 输出真实科研统计结果
- 替代 R / Python 人工统计分析
- 进行 Web 页面操作

## 6. 下一项任务

下一项任务：

> **Rule Engine V0.1 + 第一个 YAML Template**

第一版只需要支持一种明确组合：

```text
cross_sectional
+
binary outcome
+
logistic_regression
```

并稳定选择：

```text
cross_sectional_binary_logistic_v1.yaml
```

不支持的组合必须 Fail Closed。
