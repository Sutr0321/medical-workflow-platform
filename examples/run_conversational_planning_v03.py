import sys
from pathlib import Path


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


from medflow.conversation.commands import (
    PlanningCommandRouterV03,
)
from medflow.conversation.finalizer import (
    ConversationalPlanningFinalizerV03,
)
from medflow.conversation.preview import (
    ResearchPlanPreviewV03,
)
from medflow.conversation.session_service import (
    PlanningSessionServiceV03,
)
from medflow.conversation.store_v03 import (
    ConversationPlanningStoreV03,
)


def print_assistant(
    session,
):

    message = (
        session.messages[-1].content
    )

    print()
    print("AI：")
    print(message)


def show_preview(
    session,
):

    print()
    print(
        ResearchPlanPreviewV03
        .render(
            session.current_candidate,
            session.confirmed_fields,
        )
    )
    print()
    print(
        f"当前状态：{session.status}"
    )


def ask_yes_no(
    prompt: str,
) -> bool:

    while True:

        value = input(
            prompt
        ).strip().lower()

        if value in {
            "y",
            "yes",
            "是",
            "确认",
        }:
            return True

        if value in {
            "n",
            "no",
            "否",
            "取消",
        }:
            return False

        print(
            "请输入 y/n，或“确认/取消”。"
        )


def read_initial_topic() -> str:
    """
    首轮支持真正的多行提示词。

    之前直接用 input() 时，用户粘贴多行内容，
    Python 只会把第一行作为 topic，
    后续各行会被误当成后续对话消息。

    现在统一使用 /send（或“发送”）结束首轮输入。
    """

    print(
        "请先输入课题主题或完整研究方案。"
    )
    print(
        "支持多行粘贴；全部输入完成后，"
        "请单独输入一行 /send（或“发送”）提交。"
    )
    print()

    lines: list[str] = []

    while True:

        line = input(
            "你："
            if not lines
            else ""
        )

        if (
            line.strip().lower()
            in {
                "/send",
                "发送",
            }
        ):

            break

        lines.append(
            line
        )

    topic = (
        "\n".join(lines)
        .strip()
    )

    if not topic:
        raise RuntimeError(
            "课题主题不能为空。"
        )

    return topic


print()
print("========================================")
print(" 医学数据分析工作流平台")
print(" Conversational Research Planning V0.3")
print("========================================")
print()
print(
    "你只需要像聊天一样讨论课题。"
)
print(
    "首轮支持多行研究方案；使用 /send 提交。"
)
print(
    "会话中可随时输入：预览方案 / 冻结方案 / 退出"
)
print()

topic = read_initial_topic()


service = (
    PlanningSessionServiceV03()
)

print()
print(
    "正在建立 Research Planning Session……"
)

session = service.start(
    topic
)

print_assistant(
    session
)


while True:

    print()

    user_message = input(
        "你："
    ).strip()

    if not user_message:
        continue

    command = (
        PlanningCommandRouterV03
        .route(user_message)
    )

    if command == "SEND":

        print()
        print(
            "当前会话中的单行回复按回车即可提交；"
            "/send 仅用于首轮多行输入，不会发送给 AI。"
        )

        continue

    if command == "QUIT":

        print()
        print(
            "本次会话未冻结，已退出。"
        )

        break

    if command == "PREVIEW":

        show_preview(
            session
        )

        continue

    if command == "FREEZE":

        show_preview(
            session
        )

        if (
            session.status
            != "READY_TO_FREEZE"
        ):

            print()
            print(
                "当前方案还有关键内容没有讨论清楚，"
                "暂时不能冻结。"
            )
            print(
                "继续和 AI 对话即可。"
            )

            continue

        print()
        print(
            "冻结后当前版本不再直接修改；"
            "未来修改应创建新版本。"
        )

        if not ask_yes_no(
            "确认冻结以上 Research Plan？ [y/n]："
        ):

            print(
                "已取消冻结，可以继续讨论。"
            )

            continue

        (
            session,
            review_log,
            frozen_plan,
        ) = (
            ConversationalPlanningFinalizerV03
            .finalize(
                session=session,
                reviewed_by="demo_user",
            )
        )

        store = (
            ConversationPlanningStoreV03(
                project_root
                / "artifacts"
                / "conversations_v03"
            )
        )

        output_dir = (
            store.save_final_bundle(
                session=session,
                review_log=review_log,
                frozen_plan=frozen_plan,
            )
        )

        print()
        print("========================================")
        print(" Research Plan 已正式冻结")
        print("========================================")
        print()
        print(
            f"Plan ID：{frozen_plan.plan_id}"
        )
        print(
            f"Version：V{frozen_plan.plan_version}"
        )
        print(
            f"Content Hash：{frozen_plan.content_hash}"
        )
        print()
        print(
            "保存位置："
        )
        print(
            output_dir
        )
        print()
        print(
            "下一阶段将进行 Data Binding。"
        )

        break

    session = (
        service.continue_dialogue(
            session=session,
            user_message=user_message,
        )
    )

    print_assistant(
        session
    )

    if (
        session.status
        == "READY_TO_FREEZE"
    ):

        print()
        print(
            "（当前方案的核心字段已经完整。"
            "你可以继续讨论修改，"
            "也可以输入“预览方案”或“冻结方案”。）"
        )
