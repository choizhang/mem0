import os
import asyncio
import warnings

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from mem0 import MemoryClient

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Import default configuration
from mem0.configs.default import get_config

# Get default configuration and customize for healthcare assistant
config = get_config()

# Update vector store configuration
config["vector_store"]["config"]["collection_name"] = "healthcare_memories"

# Initialize Mem0 client with configuration
mem0_client = Memory.from_config(config)

# Define Memory Tools
def save_patient_info(information: str) -> dict:
    """将重要的患者信息存储到记忆中。"""
    print(f"调用save_patient_info函数存储病例: {information[:30]}...")

    # Get user_id from session state or use default
    user_id = getattr(save_patient_info, "user_id", "default_user")

    # Store in Mem0
    mem0_client.add(
        [{"role": "user", "content": information}],
        user_id=user_id,
        run_id="healthcare_session",
        metadata={"type": "patient_information"},
    )
    print(f"Mem0 response: {response}")

    return {"status": "success", "message": "Information saved"}


def retrieve_patient_info(query: str) -> str:
    """从记忆中检索相关的患者信息。"""
    print(f"调用retrieve_patient_info函数从病例里搜索: {query}")

    # Get user_id from session state or use default
    user_id = getattr(retrieve_patient_info, "user_id", "default_user")

    # Search Mem0
    results = mem0_client.search(
        query,
        user_id=user_id,
        run_id="healthcare_session",
        limit=5,
        threshold=0.7,  # Higher threshold for more relevant results
    )

    if not results or not results.get('results'):
        return "我没有关于这个话题的相关记忆。"

    memories = [f"• {memory['memory']}" for memory in results.get('results', [])]
    return "以下是我记得可能相关的信息：\n" + "\n".join(memories)


# Define Healthcare Tools
def schedule_appointment(date: str, time: str, reason: str) -> dict:
    """预约医生就诊。这个函数并未调用mem0方法"""
    # In a real app, this would connect to a scheduling system
    appointment_id = f"APT-{hash(date + time) % 10000}"

    return {
        "status": "success",
        "appointment_id": appointment_id,
        "confirmation": f"Appointment scheduled for {date} at {time} for {reason}",
        "message": "请提前15分钟到达以完成签到打卡。"
    }


# Create the Healthcare Assistant Agent
healthcare_agent = Agent(
    name="healthcare_assistant",
    model="gemini-2.0-flash",  # 使用 Gemini 作为医疗助手模型
    description="帮助患者获取健康信息和预约就诊的医疗助手。",
    instruction="""您是一位具有记忆功能的医疗助手。

您的主要职责是：
1. 当患者分享症状、病情或偏好时，使用'save_patient_info'工具记住患者信息。
2. 在当前对话相关时，使用'retrieve_patient_info'工具检索过去的患者信息。
3. 使用'schedule_appointment'工具帮助预约就诊。

重要指南：
- 始终保持同理心、专业性和帮助性。
- 保存重要的患者信息，如症状、病情、过敏史和偏好。
- 在询问患者可能已经分享过的细节之前，检查是否有相关的患者信息。
- 明确表示您不是医生，不能提供医疗诊断或治疗。
- 对于严重症状，始终建议咨询专业医疗人员。
- 对所有患者信息保密。
""",
    tools=[save_patient_info, retrieve_patient_info, schedule_appointment],
)

# Set Up Session and Runner
session_service = InMemorySessionService()

# Define constants for the conversation
APP_NAME = "healthcare_assistant_app"
USER_ID = "李雷"
SESSION_ID = "session_001"

# Create a session
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

# Create the runner
runner = Runner(agent=healthcare_agent, app_name=APP_NAME, session_service=session_service)


# Interact with the Healthcare Assistant
async def call_agent_async(query, runner, user_id, session_id):
    """向代理发送查询并返回最终响应。"""
    # print(f"\n>>> 患者: {query}")

    # Format the user's message
    content = types.Content(role="user", parts=[types.Part(text=query)])

    # Set user_id for tools to access
    save_patient_info.user_id = user_id
    retrieve_patient_info.user_id = user_id

    # Run the agent
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                response = event.content.parts[0].text
                print(f"<<< 助手: {response}")
                return response

    return "No response received."


# Example conversation flow
async def run_conversation():
    """运行演示对话流程。"""
    # 第一次交互 - 患者介绍自己的基本信息
    await call_agent_async(
        "你好，我是李雷。我这周一直在头痛，而且我对青霉素过敏。",
        runner=runner,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    # 请求健康信息
    await call_agent_async(
        "你能告诉我更多关于可能导致我头痛的原因吗？",
        runner=runner,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    # 预约就诊
    await call_agent_async(
        "我觉得我应该去看医生。你能帮我预约下周一下午2点的门诊吗？",
        runner=runner,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    # 测试记忆功能 - 应该记住患者姓名、症状和过敏史
    await call_agent_async(
        "对于我的头痛，我应该避免使用哪些药物？",
        runner=runner,
        user_id=USER_ID,
        session_id=SESSION_ID
    )


# Interactive mode
async def interactive_mode():
    """运行与医疗助手的交互式聊天会话。"""
    print("=== 医疗助手交互模式 ===")
    print("输入'exit'可随时退出。")

    # 获取用户信息
    patient_id = input("请输入患者ID（直接回车使用默认值）：").strip() or USER_ID
    session_id = f"session_{hash(patient_id) % 1000:03d}"

    # Create session for this user
    session_service.create_session(app_name=APP_NAME, user_id=patient_id, session_id=session_id)

    print(f"\n正在与患者 ID: {patient_id} 开始对话")
    print("输入您的消息并按回车键。")

    while True:
        user_input = input("\n>>> 患者: ").strip()
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("对话结束。谢谢！")
            break

        await call_agent_async(user_input, runner=runner, user_id=patient_id, session_id=session_id)


# Main execution
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='具有记忆功能的医疗助手')
    parser.add_argument('--demo', action='store_true', help='运行演示对话')
    parser.add_argument('--interactive', action='store_true', help='运行交互模式')
    parser.add_argument('--patient-id', type=str, default=USER_ID, help='对话中使用的患者ID')
    args = parser.parse_args()

    if args.demo:
        asyncio.run(run_conversation())
    elif args.interactive:
        asyncio.run(interactive_mode())
    else:
        # Default to demo mode if no arguments provided
        asyncio.run(run_conversation())
