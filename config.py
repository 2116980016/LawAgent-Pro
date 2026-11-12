import os
from dotenv import load_dotenv

load_dotenv()

ALIYUN_API_KEY = os.getenv("DASHSCOPE_API_KEY")
if not ALIYUN_API_KEY:
    raise ValueError("【安全警告】未找到 DASHSCOPE_API_KEY！请在 .env 文件中配置。")

LLM_MODEL = "deepseek-v4.1-flash"
EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"
FAISS_DB_PATH = "vectorstore/db_faiss"
LAW_FILE_PATH = "law.txt"