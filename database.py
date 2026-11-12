import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import EMBEDDING_MODEL, FAISS_DB_PATH, LAW_FILE_PATH

def get_ensemble_retriever():
    print("【初始化】正在准备检索器...")
    
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'local_files_only': True}
    )
    
    # 如果有本地缓存，直接加载（这就是加速冷启动的秘诀）
    if os.path.exists(FAISS_DB_PATH):
        print(f"【初始化】检测到本地索引 {FAISS_DB_PATH}，正在加载...")
        vectorstore = FAISS.load_local(
            FAISS_DB_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        loader = TextLoader(LAW_FILE_PATH, encoding="utf-8")
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(documents)
    else:
        print("【初始化】未找到缓存，正在读取法律文本并重新构建索引...")
        loader = TextLoader(LAW_FILE_PATH, encoding="utf-8")
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(documents)
        
        vectorstore = FAISS.from_documents(chunks, embeddings)
        os.makedirs(os.path.dirname(FAISS_DB_PATH), exist_ok=True)
        vectorstore.save_local(FAISS_DB_PATH)
        print(f"【初始化】索引构建完成，已保存至本地！")

    # 双路混合检索：向量 + BM25
    vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    bm25_retriever = BM25Retriever.from_documents(chunks)
    bm25_retriever.k = 5
    
    return EnsembleRetriever(
        retrievers=[vector_retriever, bm25_retriever], 
        weights=[0.5, 0.5]
    )

if __name__ == "__main__":
    retriever = get_ensemble_retriever()
    print("【测试】检索器组装成功！")