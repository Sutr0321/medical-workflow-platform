import json
import sys

from datetime import (
    datetime,
    timezone,
)

from pathlib import Path

from pydantic import (
    ValidationError,
)


# ==========================================
# 项目路径
# ==========================================

project_root = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

src_path = (
    project_root
    / "src"
)

sys.path.insert(
    0,
    str(src_path),
)


# ==========================================
# 项目模块
# ==========================================

from medflow.contracts.algorithm_io import (
    AlgorithmEstimateV01,
    AlgorithmInputV01,
    AlgorithmOutputV01,
)

from medflow.contracts.result import (
    ResultRecordV01,
)


# ==========================================
# 1. Algorithm Input
# ==========================================

print()
print("==============================")
print("测试 Algorithm Input Schema")
print("==============================")
print()

algorithm_input = (
    AlgorithmInputV01(
        algorithm_version="0.1.0",

        dataset_ref="demo_dataset",

        outcome_column="hypertension",

        exposure_column="vitamin_d",

        covariate_columns=[
            "age",
            "sex",
            "bmi",
        ],
    )
)

print(
    "PASS：Algorithm Input 合法"
)

print(
    json.dumps(
        algorithm_input.model_dump(
            mode="json"
        ),
        ensure_ascii=False,
        indent=2,
    )
)


# ==========================================
# 2. Algorithm Estimate
# ==========================================

estimate = (
    AlgorithmEstimateV01(
        term="vitamin_d",

        measure="odds_ratio",

        estimate=0.92,

        ci_level=0.95,

        ci_lower=0.87,

        ci_upper=0.98,

        p_value=0.012,
    )
)


# ==========================================
# 3. Algorithm Output
# ==========================================

print()
print("==============================")
print("测试 Algorithm Output Schema")
print("==============================")
print()

algorithm_output = (
    AlgorithmOutputV01(
        algorithm_version="0.1.0",

        status="SUCCESS",

        n_used=3256,

        estimates=[
            estimate
        ],

        warnings=[],

        error_message=None,
    )
)

print(
    "PASS：Algorithm Output 合法"
)

print(
    json.dumps(
        algorithm_output.model_dump(
            mode="json"
        ),
        ensure_ascii=False,
        indent=2,
    )
)


# ==========================================
# 4. Result Schema
# ==========================================

print()
print("==============================")
print("测试 Result Schema")
print("==============================")
print()

result = (
    ResultRecordV01(
        result_id="RESULT-DEMO-001",

        spec_id="RS-DEMO-001",

        spec_version=1,

        algorithm_name=(
            algorithm_output
            .algorithm_name
        ),

        algorithm_version=(
            algorithm_output
            .algorithm_version
        ),

        status=(
            algorithm_output
            .status
        ),

        n_used=(
            algorithm_output
            .n_used
        ),

        estimates=(
            algorithm_output
            .estimates
        ),

        created_at=(
            datetime.now(
                timezone.utc
            )
        ),
    )
)

print(
    "PASS：Result Record 合法"
)

print(
    json.dumps(
        result.model_dump(
            mode="json"
        ),
        ensure_ascii=False,
        indent=2,
    )
)


# ==========================================
# 5. 非法 P 值
# ==========================================

print()
print("==============================")
print("测试非法 P 值")
print("==============================")
print()

try:

    AlgorithmEstimateV01(
        term="vitamin_d",

        estimate=0.92,

        ci_lower=0.87,

        ci_upper=0.98,

        p_value=1.5,
    )

    print(
        "ERROR：非法 P 值没有被阻止"
    )

except ValidationError:

    print(
        "PASS：P 值超过 1，"
        "已被 Schema 自动阻止"
    )


# ==========================================
# 6. 缺失 Outcome Column
# ==========================================

print()
print("==============================")
print("测试缺少 Outcome Column")
print("==============================")
print()

try:

    AlgorithmInputV01(
        algorithm_version="0.1.0",

        dataset_ref="demo_dataset",

        exposure_column="vitamin_d",

        covariate_columns=[
            "age",
            "sex",
            "bmi",
        ],
    )

    print(
        "ERROR：缺少 outcome_column "
        "却通过了检查"
    )

except ValidationError:

    print(
        "PASS：缺少 outcome_column，"
        "已被 Schema 自动阻止"
    )


# ==========================================
# 7. 非法样本量
# ==========================================

print()
print("==============================")
print("测试非法样本量")
print("==============================")
print()

try:

    AlgorithmOutputV01(
        algorithm_version="0.1.0",

        status="SUCCESS",

        n_used=-1,

        estimates=[],
    )

    print(
        "ERROR：负数样本量没有被阻止"
    )

except ValidationError:

    print(
        "PASS：负数样本量已被 Schema 自动阻止"
    )


# ==========================================
# 8. 非法 spec_version
# ==========================================

print()
print("==============================")
print("测试非法 Spec Version")
print("==============================")
print()

try:

    ResultRecordV01(
        result_id="RESULT-INVALID",

        spec_id="RS-INVALID",

        spec_version=0,

        algorithm_name="logistic_regression",

        algorithm_version="0.1.0",

        status="SUCCESS",

        n_used=100,

        estimates=[],

        created_at=datetime.now(
            timezone.utc
        ),
    )

    print(
        "ERROR：spec_version=0 "
        "没有被阻止"
    )

except ValidationError:

    print(
        "PASS：非法 spec_version "
        "已被 Schema 自动阻止"
    )


# ==========================================
# 完成
# ==========================================

print()
print("==============================")
print("Schema Contract V0.1 验收完成")
print("==============================")