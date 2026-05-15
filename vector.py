import sys

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
model = os.getenv("EBM")

# =========================================
# 预处理
# ========================================= 
if len(sys.argv) < 2:
    print("请输入文件名")
    sys.exit(1)

# =========================================
# 读取知识库
# =========================================  
filename = sys.argv[1]
with open(filename, "r", encoding="utf-8") as f:
    text = f.read()

# =========================================
# 创建 Document
# =========================================
docs = [
    Document(
        page_content=text,
        metadata={
            "source": filename
        }
    )
]

# =========================================
# 文本切分
# =========================================
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

split_docs = splitter.split_documents(docs)

print("文档切分数量:", len(split_docs))

# =========================================
# Embedding 模型
# =========================================
embeddings = DashScopeEmbeddings(
    dashscope_api_key=api_key,
    model=model,
)

# =========================================
# 创建向量数据库
# =========================================
vectorstore = Chroma.from_documents(
    documents=split_docs,
    embedding=embeddings,
    persist_directory="./chroma_db"
)
print("向量数据库创建完成")