"""
index.py — Sprint 1: Build RAG Index
====================================
<<<<<<< HEAD
Mục tiêu Sprint 1 (60 phút):
=======
Mục tiêu Sprint 1:
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
  - Đọc và preprocess tài liệu từ data/docs/
  - Chunk tài liệu theo cấu trúc tự nhiên (heading/section)
  - Gắn metadata: source, section, department, effective_date, access
  - Embed và lưu vào vector store (ChromaDB)
<<<<<<< HEAD

Definition of Done Sprint 1:
  ✓ Script chạy được và index đủ docs
  ✓ Có ít nhất 3 metadata fields hữu ích cho retrieval
  ✓ Có thể kiểm tra chunk bằng list_chunks()
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# CẤU HÌNH
# =============================================================================

DOCS_DIR = Path(__file__).parent / "data" / "docs"
CHROMA_DB_DIR = Path(__file__).parent / "chroma_db"

# TODO Sprint 1: Điều chỉnh chunk size và overlap theo quyết định của nhóm
# Gợi ý từ slide: chunk 300-500 tokens, overlap 50-80 tokens
CHUNK_SIZE = 400       # tokens (ước lượng bằng số ký tự / 4)
CHUNK_OVERLAP = 80     # tokens overlap giữa các chunk


# =============================================================================
# STEP 1: PREPROCESS
# Làm sạch text trước khi chunk và embed
# =============================================================================

def preprocess_document(raw_text: str, filepath: str) -> Dict[str, Any]:
    """
    Preprocess một tài liệu: extract metadata từ header và làm sạch nội dung.

    Args:
        raw_text: Toàn bộ nội dung file text
        filepath: Đường dẫn file để làm source mặc định

    Returns:
        Dict chứa:
          - "text": nội dung đã clean
          - "metadata": dict với source, department, effective_date, access

    TODO Sprint 1:
    - Extract metadata từ dòng đầu file (Source, Department, Effective Date, Access)
    - Bỏ các dòng header metadata khỏi nội dung chính
    - Normalize khoảng trắng, xóa ký tự rác

    Gợi ý: dùng regex để parse dòng "Key: Value" ở đầu file.
    """
=======
"""

import os
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import re
from pathlib import Path
from typing import List, Dict, Any

import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

DOCS_DIR = Path.cwd() / "data" / "docs"
CHROMA_DB_DIR = Path.cwd() / "chroma_db"

CHUNK_SIZE = 400
CHUNK_OVERLAP = 80

_embedding_model = None


def preprocess_document(raw_text: str, filepath: str) -> Dict[str, Any]:
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
    lines = raw_text.strip().split("\n")
    metadata = {
        "source": filepath,
        "section": "",
        "department": "unknown",
        "effective_date": "unknown",
        "access": "internal",
    }
<<<<<<< HEAD
=======

>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
    content_lines = []
    header_done = False

    for line in lines:
<<<<<<< HEAD
        if not header_done:
            # TODO: Parse metadata từ các dòng "Key: Value"
            # Ví dụ: "Source: policy/refund-v4.pdf" → metadata["source"] = "policy/refund-v4.pdf"
            if line.startswith("Source:"):
                metadata["source"] = line.replace("Source:", "").strip()
            elif line.startswith("Department:"):
                metadata["department"] = line.replace("Department:", "").strip()
            elif line.startswith("Effective Date:"):
                metadata["effective_date"] = line.replace("Effective Date:", "").strip()
            elif line.startswith("Access:"):
                metadata["access"] = line.replace("Access:", "").strip()
            elif line.startswith("==="):
                # Gặp section heading đầu tiên → kết thúc header
                header_done = True
                content_lines.append(line)
            elif line.strip() == "" or line.isupper():
                # Dòng tên tài liệu (toàn chữ hoa) hoặc dòng trống
                continue
=======
        stripped = line.strip()

        if not header_done:
            if stripped.startswith("Source:"):
                metadata["source"] = stripped.replace("Source:", "", 1).strip()
            elif stripped.startswith("Department:"):
                metadata["department"] = stripped.replace("Department:", "", 1).strip()
            elif stripped.startswith("Effective Date:"):
                metadata["effective_date"] = stripped.replace("Effective Date:", "", 1).strip()
            elif stripped.startswith("Access:"):
                metadata["access"] = stripped.replace("Access:", "", 1).strip()
            elif stripped.startswith("==="):
                header_done = True
                content_lines.append(line)
            elif stripped == "" or stripped.isupper():
                continue
            else:
                header_done = True
                content_lines.append(line)
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
        else:
            content_lines.append(line)

    cleaned_text = "\n".join(content_lines)
<<<<<<< HEAD

    # TODO: Thêm bước normalize text nếu cần
    # Gợi ý: bỏ ký tự đặc biệt thừa, chuẩn hóa dấu câu
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)  # max 2 dòng trống liên tiếp
=======
    cleaned_text = re.sub(r"[ \t]+", " ", cleaned_text)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text).strip()
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba

    return {
        "text": cleaned_text,
        "metadata": metadata,
    }


<<<<<<< HEAD
# =============================================================================
# STEP 2: CHUNK
# Chia tài liệu thành các đoạn nhỏ theo cấu trúc tự nhiên
# =============================================================================

def chunk_document(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Chunk một tài liệu đã preprocess thành danh sách các chunk nhỏ.

    Args:
        doc: Dict với "text" và "metadata" (output của preprocess_document)

    Returns:
        List các Dict, mỗi dict là một chunk với:
          - "text": nội dung chunk
          - "metadata": metadata gốc + "section" của chunk đó

    TODO Sprint 1:
    1. Split theo heading "=== Section ... ===" hoặc "=== Phần ... ===" trước
    2. Nếu section quá dài (> CHUNK_SIZE * 4 ký tự), split tiếp theo paragraph
    3. Thêm overlap: lấy đoạn cuối của chunk trước vào đầu chunk tiếp theo
    4. Mỗi chunk PHẢI giữ metadata đầy đủ từ tài liệu gốc

    Gợi ý: Ưu tiên cắt tại ranh giới tự nhiên (section, paragraph)
    thay vì cắt theo token count cứng.
    """
    text = doc["text"]
    base_metadata = doc["metadata"].copy()
    chunks = []

    # TODO: Implement chunking theo section heading
    # Bước 1: Split theo heading pattern "=== ... ==="
=======
def chunk_document(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    text = doc["text"]
    base_metadata = doc["metadata"].copy()
    chunks: List[Dict[str, Any]] = []

>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
    sections = re.split(r"(===.*?===)", text)

    current_section = "General"
    current_section_text = ""

    for part in sections:
<<<<<<< HEAD
        if re.match(r"===.*?===", part):
            # Lưu section trước (nếu có nội dung)
            if current_section_text.strip():
                section_chunks = _split_by_size(
                    current_section_text.strip(),
                    base_metadata=base_metadata,
                    section=current_section,
                )
                chunks.extend(section_chunks)
            # Bắt đầu section mới
=======
        if re.fullmatch(r"===.*?===", part.strip()):
            if current_section_text.strip():
                chunks.extend(
                    _split_by_size(
                        current_section_text.strip(),
                        base_metadata=base_metadata,
                        section=current_section,
                    )
                )
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
            current_section = part.strip("= ").strip()
            current_section_text = ""
        else:
            current_section_text += part

<<<<<<< HEAD
    # Lưu section cuối cùng
    if current_section_text.strip():
        section_chunks = _split_by_size(
            current_section_text.strip(),
            base_metadata=base_metadata,
            section=current_section,
        )
        chunks.extend(section_chunks)
=======
    if current_section_text.strip():
        chunks.extend(
            _split_by_size(
                current_section_text.strip(),
                base_metadata=base_metadata,
                section=current_section,
            )
        )
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba

    return chunks


def _split_by_size(
    text: str,
<<<<<<< HEAD
    base_metadata: Dict,
=======
    base_metadata: Dict[str, Any],
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
    section: str,
    chunk_chars: int = CHUNK_SIZE * 4,
    overlap_chars: int = CHUNK_OVERLAP * 4,
) -> List[Dict[str, Any]]:
<<<<<<< HEAD
    """
    Helper: Split text dài thành chunks với overlap (theo paragraph).
    """
    if len(text) <= chunk_chars:
        # Toàn bộ section vừa một chunk
=======
    if len(text) <= chunk_chars:
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
        return [{
            "text": text,
            "metadata": {**base_metadata, "section": section},
        }]

<<<<<<< HEAD
    chunks = []
    # Split theo paragraph
    paragraphs = text.split("\n\n")
    current_chunk_text = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        if len(current_chunk_text) + len(para) + 2 <= chunk_chars:
            current_chunk_text += ("\n\n" + para) if current_chunk_text else para
        else:
            if current_chunk_text:
                chunks.append({
                    "text": current_chunk_text,
                    "metadata": {**base_metadata, "section": section},
                })
                # Giữ lại một phần của chunk trước để làm overlap
                # Lấy số ký tự overlap, ưu tiên cắt đúng từ thay vì cắt ngang chữ
                if len(current_chunk_text) > overlap_chars:
                    overlap_start = current_chunk_text.rfind(" ", 0, len(current_chunk_text) - overlap_chars)
                    if overlap_start == -1: overlap_start = len(current_chunk_text) - overlap_chars
                    overlap_text = current_chunk_text[overlap_start:].strip()
                else:
                    overlap_text = current_chunk_text
                
                current_chunk_text = overlap_text + "\n\n" + para if overlap_text else para
            else:
                chunks.append({
                    "text": para,
                    "metadata": {**base_metadata, "section": section},
                })
                current_chunk_text = ""
                
    if current_chunk_text:
        chunks.append({
            "text": current_chunk_text,
=======
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [text]

    chunks: List[Dict[str, Any]] = []
    current = ""

    for para in paragraphs:
        candidate = para if not current else current + "\n\n" + para
        if len(candidate) <= chunk_chars:
            current = candidate
            continue

        if current:
            chunks.append({
                "text": current,
                "metadata": {**base_metadata, "section": section},
            })

            overlap_text = current[-overlap_chars:] if overlap_chars < len(current) else current
            current = (overlap_text + "\n\n" + para).strip()
        else:
            current = para

        while len(current) > chunk_chars:
            piece = current[:chunk_chars]
            chunks.append({
                "text": piece,
                "metadata": {**base_metadata, "section": section},
            })
            current = current[chunk_chars - overlap_chars:].strip()

    if current.strip():
        chunks.append({
            "text": current.strip(),
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
            "metadata": {**base_metadata, "section": section},
        })

    return chunks


<<<<<<< HEAD
# =============================================================================
# STEP 3: EMBED + STORE
# Embed các chunk và lưu vào ChromaDB
# =============================================================================

def get_embedding(text: str) -> List[float]:
    """
    Tạo embedding vector cho một đoạn text bằng Sentence Transformers.
    """
    from sentence_transformers import SentenceTransformer
    global _embedding_model
    if "_embedding_model" not in globals():
        print("[Load Model] Loading paraphrase-multilingual-MiniLM-L12-v2...")
        _embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return _embedding_model.encode(text).tolist()


def build_index(docs_dir: Path = DOCS_DIR, db_dir: Path = CHROMA_DB_DIR) -> None:
    """
    Pipeline hoàn chỉnh: đọc docs → preprocess → chunk → embed → store.
    """
    import chromadb

=======
def get_embedding(text: str) -> List[float]:
    global _embedding_model

    text = text.strip()
    if not text:
        return []

    if _embedding_model is None:
        print("[Load Model] Loading paraphrase-multilingual-MiniLM-L12-v2...")
        _embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    return _embedding_model.encode(text, normalize_embeddings=True).tolist()


def build_index(docs_dir: Path = DOCS_DIR, db_dir: Path = CHROMA_DB_DIR) -> None:
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
    print(f"Đang build index từ: {docs_dir}")
    db_dir.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(db_dir))
    collection = client.get_or_create_collection(
        name="rag_lab",
<<<<<<< HEAD
        metadata={"hnsw:space": "cosine"}
    )

    total_chunks = 0
    doc_files = list(docs_dir.glob("*.txt"))
=======
        metadata={"hnsw:space": "cosine"},
    )

    total_chunks = 0
    doc_files = sorted(docs_dir.glob("*.txt"))
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba

    if not doc_files:
        print(f"Không tìm thấy file .txt trong {docs_dir}")
        return

    for filepath in doc_files:
        print(f"  Processing: {filepath.name}")
        raw_text = filepath.read_text(encoding="utf-8")

        doc = preprocess_document(raw_text, str(filepath))
        chunks = chunk_document(doc)

        ids = []
        embeddings = []
        documents = []
        metadatas = []
<<<<<<< HEAD
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{filepath.stem}_{i}"
            embedding = get_embedding(chunk["text"])
            
=======

        for i, chunk in enumerate(chunks):
            chunk_id = f"{filepath.stem}_{i}"
            try:
                embedding = get_embedding(chunk["text"])
            except Exception as e:
                print(f"    ! Lỗi embedding ở chunk {chunk_id}: {e}")
                continue

>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
            ids.append(chunk_id)
            embeddings.append(embedding)
            documents.append(chunk["text"])
            metadatas.append(chunk["metadata"])
<<<<<<< HEAD
            
=======

>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
        if ids:
            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )

<<<<<<< HEAD
        print(f"    → {len(chunks)} chunks đã được lưu")
        total_chunks += len(chunks)
=======
        print(f"    → {len(ids)} chunks đã được lưu")
        total_chunks += len(ids)
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba

    print(f"\nHoàn thành! Tổng số chunks: {total_chunks}")


<<<<<<< HEAD
# =============================================================================
# STEP 4: INSPECT / KIỂM TRA
# Dùng để debug và kiểm tra chất lượng index
# =============================================================================

def list_chunks(db_dir: Path = CHROMA_DB_DIR, n: int = 5) -> None:
    """
    In ra n chunk đầu tiên trong ChromaDB để kiểm tra chất lượng index.

    TODO Sprint 1:
    Implement sau khi hoàn thành build_index().
    Kiểm tra:
    - Chunk có giữ đủ metadata không? (source, section, effective_date)
    - Chunk có bị cắt giữa điều khoản không?
    - Metadata effective_date có đúng không?
    """
    try:
        import chromadb
=======
def list_chunks(db_dir: Path = CHROMA_DB_DIR, n: int = 5) -> None:
    try:
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
        client = chromadb.PersistentClient(path=str(db_dir))
        collection = client.get_collection("rag_lab")
        results = collection.get(limit=n, include=["documents", "metadatas"])

        print(f"\n=== Top {n} chunks trong index ===\n")
<<<<<<< HEAD
        for i, (doc, meta) in enumerate(zip(results["documents"], results["metadatas"])):
            print(f"[Chunk {i+1}]")
=======
        for i, (doc, meta) in enumerate(zip(results["documents"], results["metadatas"]), 1):
            print(f"[Chunk {i}]")
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
            print(f"  Source: {meta.get('source', 'N/A')}")
            print(f"  Section: {meta.get('section', 'N/A')}")
            print(f"  Effective Date: {meta.get('effective_date', 'N/A')}")
            print(f"  Text preview: {doc[:120]}...")
            print()
    except Exception as e:
        print(f"Lỗi khi đọc index: {e}")
        print("Hãy chạy build_index() trước.")


def inspect_metadata_coverage(db_dir: Path = CHROMA_DB_DIR) -> None:
<<<<<<< HEAD
    """
    Kiểm tra phân phối metadata trong toàn bộ index.

    Checklist Sprint 1:
    - Mọi chunk đều có source?
    - Có bao nhiêu chunk từ mỗi department?
    - Chunk nào thiếu effective_date?

    TODO: Implement sau khi build_index() hoàn thành.
    """
    try:
        import chromadb
=======
    try:
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
        client = chromadb.PersistentClient(path=str(db_dir))
        collection = client.get_collection("rag_lab")
        results = collection.get(include=["metadatas"])

        print(f"\nTổng chunks: {len(results['metadatas'])}")

<<<<<<< HEAD
        # TODO: Phân tích metadata
        # Đếm theo department, kiểm tra effective_date missing, v.v.
        departments = {}
        missing_date = 0
=======
        departments = {}
        missing_date = 0

>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
        for meta in results["metadatas"]:
            dept = meta.get("department", "unknown")
            departments[dept] = departments.get(dept, 0) + 1
            if meta.get("effective_date") in ("unknown", "", None):
                missing_date += 1

        print("Phân bố theo department:")
        for dept, count in departments.items():
            print(f"  {dept}: {count} chunks")
        print(f"Chunks thiếu effective_date: {missing_date}")

    except Exception as e:
        print(f"Lỗi: {e}. Hãy chạy build_index() trước.")


<<<<<<< HEAD
# =============================================================================
# MAIN
# =============================================================================

=======
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
if __name__ == "__main__":
    print("=" * 60)
    print("Sprint 1: Build RAG Index")
    print("=" * 60)

<<<<<<< HEAD
    # Bước 1: Kiểm tra docs
    doc_files = list(DOCS_DIR.glob("*.txt"))
=======
    doc_files = sorted(DOCS_DIR.glob("*.txt"))
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
    print(f"\nTìm thấy {len(doc_files)} tài liệu:")
    for f in doc_files:
        print(f"  - {f.name}")

<<<<<<< HEAD
    # Bước 2: Test preprocess và chunking (không cần API key)
    print("\n--- Test preprocess + chunking ---")
    for filepath in doc_files[:1]:  # Test với 1 file đầu
        raw = filepath.read_text(encoding="utf-8")
        doc = preprocess_document(raw, str(filepath))
        chunks = chunk_document(doc)
        print(f"\nFile: {filepath.name}")
        print(f"  Metadata: {doc['metadata']}")
        print(f"  Số chunks: {len(chunks)}")
        for i, chunk in enumerate(chunks[:3]):
            print(f"\n  [Chunk {i+1}] Section: {chunk['metadata']['section']}")
            print(f"  Text: {chunk['text'][:150]}...")

    # Bước 3: Build index
    print("\n--- Build Full Index ---")
    build_index()

    # Bước 4: Kiểm tra index
    list_chunks()
    inspect_metadata_coverage()

    print("\nSprint 1 setup hoàn thành!")
=======
    print("\n--- Test preprocess + chunking ---")
    for filepath in doc_files[:1]:
        raw = filepath.read_text(encoding="utf-8")
        doc = preprocess_document(raw, str(filepath))
        chunks = chunk_document(doc)

        print(f"\nFile: {filepath.name}")
        print(f"  Metadata: {doc['metadata']}")
        print(f"  Số chunks: {len(chunks)}")
        for i, chunk in enumerate(chunks[:3], 1):
            print(f"\n  [Chunk {i}] Section: {chunk['metadata']['section']}")
            print(f"  Text: {chunk['text'][:150]}...")

    print("\n--- Build Full Index ---")
    build_index()

    list_chunks()
    inspect_metadata_coverage()

    print("\nSprint 1 hoàn thành!")
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
