import re
from typing import Literal


PlanningCommand = Literal[
    "FREEZE",
    "PREVIEW",
    "QUIT",
    "NONE",
]


class PlanningCommandRouterV03:
    """
    在消息进入 LLM 之前识别系统级命令。

    关键原则：
    冻结是系统状态变更，绝不能由 AI 文字回复代替。
    """

    FREEZE_PATTERNS = (
        r"^冻结$",
        r"^冻结方案$",
        r"^确认冻结$",
        r"^确认并冻结$",
        r"^帮我冻结(?:方案)?$",
        r"^请冻结(?:方案)?$",
        r"^正式冻结(?:方案)?$",
        r"^/freeze$",
    )

    PREVIEW_PATTERNS = (
        r"^预览$",
        r"^预览方案$",
        r"^看看方案$",
        r"^查看方案$",
        r"^/preview$",
    )

    QUIT_PATTERNS = (
        r"^退出$",
        r"^结束$",
        r"^/quit$",
        r"^/exit$",
    )

    @staticmethod
    def route(
        message: str,
    ) -> PlanningCommand:

        normalized = (
            message
            .strip()
            .lower()
        )

        if PlanningCommandRouterV03._matches(
            normalized,
            PlanningCommandRouterV03
            .FREEZE_PATTERNS,
        ):
            return "FREEZE"

        if PlanningCommandRouterV03._matches(
            normalized,
            PlanningCommandRouterV03
            .PREVIEW_PATTERNS,
        ):
            return "PREVIEW"

        if PlanningCommandRouterV03._matches(
            normalized,
            PlanningCommandRouterV03
            .QUIT_PATTERNS,
        ):
            return "QUIT"

        return "NONE"

    @staticmethod
    def _matches(
        value: str,
        patterns: tuple[str, ...],
    ) -> bool:

        return any(
            re.fullmatch(
                pattern,
                value,
                flags=re.IGNORECASE,
            )
            is not None
            for pattern in patterns
        )
