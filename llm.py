from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")
model = os.getenv("LLM")

llm = ChatOpenAI(
    model=model,                                            # 模型名称
    api_key=api_key,                   # API Key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",    # 阿里云兼容地址
    temperature=0.3,                                                 # 控制随机性，范围 0-2，值越大越随机
    max_tokens=2048,                                                 # 最大输出 token 数
)