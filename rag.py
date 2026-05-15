from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from llm import llm
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
model = os.getenv("EBM")


# =========================================
# 初始化向量数据库
# =========================================
embeddings = DashScopeEmbeddings(
    dashscope_api_key=api_key,
    model=model,
)

vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings,
)

# =========================================
# 创建检索器
# =========================================
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# =========================================
# 创建 RAG 查询函数
# =========================================
def format_docs(docs):
    """格式化检索到的文档"""
    return "\n\n".join(doc.page_content for doc in docs)

# ========================================
# 创建 RAG 链（用于知识库查询）
# ========================================
def query_knowledge_base(prompt: str, question: str) -> str:
    """
    从网络安全知识库中检索相关信息
    """
    # 检索相关文档
    docs = retriever.invoke(question)
    
    if not docs:
        return "知识库中没有找到相关信息"
    
    # 格式化上下文
    context = format_docs(docs)
    
    response_prompt = ChatPromptTemplate.from_template(prompt)
    
    chain = response_prompt | llm | StrOutputParser()
    return chain.invoke({"context": context, "question": question})


# ========================================
# 流式版本，返回完整的字符串（内部流式收集）
# ========================================
async def query_knowledge_base_streaming(prompt: str, question: str) -> str:
    """流式版本，返回完整的字符串（内部流式收集）"""
    docs = retriever.invoke(question)
    
    if not docs:
        return "知识库中没有找到相关信息"
    
    context = format_docs(docs)
    
    response_prompt = ChatPromptTemplate.from_template(prompt)
    
    chain = response_prompt | llm | StrOutputParser()
    
    # 收集流式输出
    full_response = ""
    async for chunk in chain.astream({"context": context, "question": question}):
        full_response += chunk
        print(chunk, end="", flush=True)  # 实时打印
    
    return full_response