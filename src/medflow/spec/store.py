from pathlib import Path

from medflow.contracts.frozen_spec import (
    FrozenResearchSpecV01,
)


class FrozenSpecStore:
    """
    V0.1 Research Spec 文件存储。

    后续可以替换成 PostgreSQL，
    但上层逻辑不用改变。
    """

    def __init__(
        self,
        root_dir: str | Path,
    ):
        self.root_dir = Path(
            root_dir
        )

    def save(
        self,
        spec: FrozenResearchSpecV01,
    ) -> Path:

        # ==========================================
        # 每个 Research Spec 一个目录
        # ==========================================

        spec_dir = (
            self.root_dir
            / spec.spec_id
        )

        spec_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # ==========================================
        # 每个版本独立文件
        # ==========================================

        file_path = (
            spec_dir
            / f"v{spec.spec_version}.json"
        )

        # ==========================================
        # 已存在则拒绝覆盖
        # ==========================================

        if file_path.exists():
            raise FileExistsError(
                f"Frozen Research Spec 已存在，"
                f"禁止覆盖：{file_path}"
            )

        file_path.write_text(
            spec.model_dump_json(
                indent=2
            ),
            encoding="utf-8",
        )

        return file_path