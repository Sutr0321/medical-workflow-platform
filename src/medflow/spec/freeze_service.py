import hashlib
import json
import uuid
from datetime import datetime, timezone

from medflow.contracts.frozen_spec import (
    FrozenResearchSpecV01,
)

from medflow.contracts.reviewed_spec import (
    ReviewedResearchSpecV01,
)


class SpecFreezeService:
    """
    Research Spec 冻结服务。

    不调用 AI。

    只有经过人工确认的 Reviewed Research Spec
    才允许冻结。
    """

    @staticmethod
    def freeze(
        reviewed_spec: ReviewedResearchSpecV01,
    ) -> FrozenResearchSpecV01:

        # ==========================================
        # 1. 必须已经完成人工确认
        # ==========================================

        if (
            reviewed_spec.review_status
            != "READY_FOR_DATA_BINDING"
        ):
            raise ValueError(
                "Research Spec 尚未完成人工确认，"
                "不能冻结。"
            )

        if not reviewed_spec.confirmation.confirmed:
            raise ValueError(
                "Research Spec 未被人工确认，"
                "不能冻结。"
            )

        # ==========================================
        # 2. 生成 Research Spec ID
        # ==========================================

        spec_id = (
            "RS-"
            + uuid.uuid4().hex[:12].upper()
        )

        # V0.1 第一版固定为 version 1
        spec_version = 1

        # ==========================================
        # 3. 计算内容 Hash
        # ==========================================

        content_hash = (
            SpecFreezeService._calculate_content_hash(
                reviewed_spec
            )
        )

        # ==========================================
        # 4. 创建 Frozen Spec
        # ==========================================

        frozen_spec = FrozenResearchSpecV01(
            spec_id=spec_id,
            spec_version=spec_version,
            status="FROZEN",
            content_hash=content_hash,
            frozen_at=datetime.now(
                timezone.utc
            ),
            research_spec=reviewed_spec,
        )

        return frozen_spec

    @staticmethod
    def _calculate_content_hash(
        spec: ReviewedResearchSpecV01,
    ) -> str:
        """
        对真正的研究方案内容进行 SHA-256。

        不把人工确认时间等系统元数据
        放进内容 Hash。
        """

        data = spec.model_dump(
            mode="json"
        )

        # ------------------------------------------
        # 删除不属于研究方案本身的运行元数据
        # ------------------------------------------

        data.pop(
            "open_issues",
            None,
        )

        data.pop(
            "review_status",
            None,
        )

        data.pop(
            "confirmation",
            None,
        )

        # ------------------------------------------
        # Canonical JSON
        # ------------------------------------------

        canonical_json = json.dumps(
            data,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

        return hashlib.sha256(
            canonical_json.encode(
                "utf-8"
            )
        ).hexdigest()