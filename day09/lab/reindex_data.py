import os
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

def reindex():
    print("🚀 Khởi động lại quá trình Indexing...")
    
    # Kết nối ChromaDB
    db_path = "./chroma_db"
    client = chromadb.PersistentClient(path=db_path)
    
    # Xóa collection cũ nếu có để làm sạch dữ liệu
    try:
        client.delete_collection("day09_docs")
        print("🗑️  Đã xóa collection cũ 'day09_docs'")
    except:
        pass
    
    col = client.get_or_create_collection(
        "day09_docs", 
        metadata={"hnsw:space": "cosine"}
    )
    
    # Load model embedding
    print("⏳ Đang tải model embedding 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    docs_dir = "./data/docs"
    files = [f for f in os.listdir(docs_dir) if f.endswith(".txt")]
    
    all_docs = []
    all_metadatas = []
    all_ids = []
    
    chunk_count = 0
    for fname in files:
        file_path = os.path.join(docs_dir, fname)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Chia nhỏ file theo đoạn (\n\n)
        # Đây là cách chia hiệu quả cho các file FAQ hoặc Policy có cấu trúc
        chunks = [c.strip() for c in content.split("\n\n") if len(c.strip()) > 50]
        
        print(f"📄 Đang xử lý {fname}: {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{fname}_{i:03d}"
            all_ids.append(chunk_id)
            all_docs.append(chunk)
            all_metadatas.append({"source": fname, "chunk_index": i})
            chunk_count += 1

    # Thêm vào ChromaDB
    print(f"📥 Đang đẩy {chunk_count} chunks vào ChromaDB...")
    
    # ChromaDB add có giới hạn kích thước batch, nhưng 100-200 chunks thì thoải mái
    col.add(
        ids=all_ids,
        documents=all_docs,
        metadatas=all_metadatas
    )
    
    print(f"✅ Hoàn thành! Đã index {chunk_count} chunks từ {len(files)} files.")

if __name__ == "__main__":
    reindex()
