import chromadb
from chromadb.utils import embedding_functions
import os
from datetime import datetime

# Khởi tạo ChromaDB lưu vào thư mục local
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Dùng embedding model nhỏ gọn, chạy được trên máy yếu
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"  # model 80MB, đủ tốt cho tiếng Anh
)

# Tạo collection lưu memory
collection = chroma_client.get_or_create_collection(
    name="chat_memory",
    embedding_function=embedding_fn
)


def save_memory(question: str, answer: str):
    """Lưu cặp hỏi-đáp vào ChromaDB"""
    memory_id = f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    collection.add(
        ids=[memory_id],
        documents=[f"Question: {question}\nAnswer: {answer[:300]}"],
        metadatas=[{
            "question": question,
            "answer": answer[:500],
            "timestamp": datetime.now().isoformat()
        }]
    )
    print(f"[Memory] Da luu: {memory_id}")


def search_memory(query: str, n_results: int = 3) -> list:
    """Tìm các memory liên quan nhất đến câu hỏi hiện tại"""
    total = collection.count()
    if total == 0:
        return []

    # Không lấy nhiều hơn số lượng đang có
    n = min(n_results, total)

    results = collection.query(
        query_texts=[query],
        n_results=n
    )

    memories = []
    if results and results["metadatas"]:
        for meta in results["metadatas"][0]:
            memories.append({
                "question": meta["question"],
                "answer": meta["answer"],
                "timestamp": meta["timestamp"]
            })

    return memories


def get_all_memories() -> list:
    """Lấy toàn bộ memory để hiển thị lên UI"""
    total = collection.count()
    if total == 0:
        return []

    results = collection.get()
    memories = []
    if results and results["metadatas"]:
        for meta in results["metadatas"]:
            memories.append({
                "question": meta["question"],
                "answer": meta["answer"],
                "timestamp": meta["timestamp"]
            })

    # Sắp xếp mới nhất lên đầu
    memories.sort(key=lambda x: x["timestamp"], reverse=True)
    return memories


def clear_memory():
    """Xóa toàn bộ memory"""
    global collection
    chroma_client.delete_collection("chat_memory")
    collection = chroma_client.get_or_create_collection(
        name="chat_memory",
        embedding_function=embedding_fn
    )
    print("[Memory] Da xoa toan bo memory")