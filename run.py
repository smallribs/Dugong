from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import yaml

# 1. 初始化模型
from llm import llm
llm = llm

# 2. 创建一个检查点保存器（用于短期记忆）
checkpointer = InMemorySaver()


@tool(description="用于查询知识库内容")
def search_knowledge(query: str) -> str:
    from rag import query_knowledge_base, query_knowledge_base_streaming
    with open("prompt.yaml", "r", encoding="utf-8") as f:
        prompt = yaml.safe_load(f)
    result = query_knowledge_base(prompt["query"], query)
    return result

@tool(description="用于修改请求报文")
def modify_request_message(raw_http_message: str) -> str:
    from rag import query_knowledge_base
    with open("prompt.yaml", "r", encoding="utf-8") as f:
        prompt = yaml.safe_load(f)
    modified_request_message = query_knowledge_base(prompt["modify_request_message"], raw_http_message)
    return modified_request_message

@tool(description="用于重放修改后请求报文")
def replay_http_message(raw_http_message: str) -> str:
    from utils import replay
    response_header = replay(raw_http_message).headers
    return response_header

# 3. 创建 Agent，并传入 checkpointer
with open("prompt.yaml", "r", encoding="utf-8") as f:
    system_prompt = yaml.safe_load(f)["system_prompt"]
    
agent = create_agent(
    model=llm,
    tools=[modify_request_message, replay_http_message, search_knowledge],  # 你的工具列表
    system_prompt=system_prompt,
    checkpointer=checkpointer  # <-- 关键：注入记忆
)

# 4. 配置会话ID (thread_id)

config = {"configurable": {"thread_id": "user_123_session_1"}}

with open("./http_request.txt", "r", encoding="utf-8") as f:
    raw_http_message = f.read()

import asyncio

async def stream_echo():
    """简洁格式的流式输出"""
    print("\n🚀 开始处理,可能会比较耗时...\n")
    
    async for chunk in agent.astream(
        {"messages": [HumanMessage(content=f"""
请处理以下HTTP报文并告诉我结果：

{raw_http_message}

要求：修改报文后重放，根据返回内容查询知识库，然后回答问题。
""")]},
        config=config
    ):
        # 提取工具调用
        if "model" in chunk and "messages" in chunk["model"]:
            for msg in chunk["model"]["messages"]:
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tool in msg.tool_calls:
                        print(f"🔧 调用 {tool['name']}...")
        
        # 提取工具返回
        elif "tools" in chunk and "messages" in chunk["tools"]:
            for msg in chunk["tools"]["messages"]:
                if isinstance(msg, ToolMessage):
                    print(f"✅ {msg.name} 返回数据")
    
    # 获取最终回答
    print("\n❗正在生成最终结果...\n")
    
    final_response = agent.invoke(
        {"messages": [HumanMessage(content="告诉我之前的测试结果")]},
        config=config
    )
    
    print("\n📝 最终回答:")
    print(final_response["messages"][-1].content)

asyncio.run(stream_echo())