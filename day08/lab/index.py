"""
index.py — Sprint 1: Build RAG Index
====================================
Mục tiêu Sprint 1:
  - Đọc và preprocess tài liệu từ data/docs/
  - Chunk tài liệu theo cấu trúc tự nhiên (heading/section)
  - Gắn metadata: source, section, department, effective_date, access
  - Embed và lưu vào vector store (ChromaDB)
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
    lines = raw_text.strip().split("\n")
    metadata = {
        "source": filepath,
        "section": "",
        "department": "unknown",
        "effective_date": "unknown",
        "access": "internal",
    }

    content_lines = []
    header_done = False

    for line in lines:
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
        else:
            content_lines.append(line)

    cleaned_text = "\n".join(content_lines)
    cleaned_text = re.sub(r"[ \t]+", " ", cleaned_text)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text).strip()

    return {
        "text": cleaned_text,
        "metadata": metadata,
    }


def chunk_document(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    text = doc["text"]
    base_metadata = doc["metadata"].copy()
    chunks: List[Dict[str, Any]] = []

    sections = re.split(r"(===.*?===)", text)

    current_section = "General"
    current_section_text = ""

    for part in sections:
        if re.fullmatch(r"===.*?===", part.strip()):
            if current_section_text.strip():
                chunks.extend(
                    _split_by_size(
                        current_section_text.strip(),
                        base_metadata=base_metadata,
                        section=current_section,
                    )
                )
            current_section = part.strip("= ").strip()
            current_section_text = ""
        else:
            current_section_text += part

    if current_section_text.strip():
        chunks.extend(
            _split_by_size(
                current_section_text.strip(),
                base_metadata=base_metadata,
                section=current_section,
            )
        )

    return chunks


def _split_by_size(
    text: str,
    base_metadata: Dict[str, Any],
    section: str,
    chunk_chars: int = CHUNK_SIZE * 4,
    overlap_chars: int = CHUNK_OVERLAP * 4,
) -> List[Dict[str, Any]]:
    if len(text) <= chunk_chars:
        return [{
            "text": text,
            "metadata": {**base_metadata, "section": section},
        }]

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
            "metadata": {**base_metadata, "section": section},
        })

    return chunks


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
    print(f"Đang build index từ: {docs_dir}")
    db_dir.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(db_dir))
    collection = client.get_or_create_collection(
        name="rag_lab",
        metadata={"hnsw:space": "cosine"},
    )

    total_chunks = 0
    doc_files = sorted(docs_dir.glob("*.txt"))

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

        for i, chunk in enumerate(chunks):
            chunk_id = f"{filepath.stem}_{i}"
            try:
                embedding = get_embedding(chunk["text"])
            except Exception as e:
                print(f"    ! Lỗi embedding ở chunk {chunk_id}: {e}")
                continue

            ids.append(chunk_id)
            embeddings.append(embedding)
            documents.append(chunk["text"])
            metadatas.append(chunk["metadata"])

        if ids:
            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )

        print(f"    → {len(ids)} chunks đã được lưu")
        total_chunks += len(ids)

    print(f"\nHoàn thành! Tổng số chunks: {total_chunks}")


def list_chunks(db_dir: Path = CHROMA_DB_DIR, n: int = 5) -> None:
    try:
        client = chromadb.PersistentClient(path=str(db_dir))
        collection = client.get_collection("rag_lab")
        results = collection.get(limit=n, include=["documents", "metadatas"])

        print(f"\n=== Top {n} chunks trong index ===\n")
        for i, (doc, meta) in enumerate(zip(results["documents"], results["metadatas"]), 1):
            print(f"[Chunk {i}]")
            print(f"  Source: {meta.get('source', 'N/A')}")
            print(f"  Section: {meta.get('section', 'N/A')}")
            print(f"  Effective Date: {meta.get('effective_date', 'N/A')}")
            print(f"  Text preview: {doc[:120]}...")
            print()
    except Exception as e:
        print(f"Lỗi khi đọc index: {e}")
        print("Hãy chạy build_index() trước.")


def inspect_metadata_coverage(db_dir: Path = CHROMA_DB_DIR) -> None:
    try:
        client = chromadb.PersistentClient(path=str(db_dir))
        collection = client.get_collection("rag_lab")
        results = collection.get(include=["metadatas"])

        print(f"\nTổng chunks: {len(results['metadatas'])}")

        departments = {}
        missing_date = 0

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


if __name__ == "__main__":
    print("=" * 60)
    print("Sprint 1: Build RAG Index")
    print("=" * 60)

    doc_files = sorted(DOCS_DIR.glob("*.txt"))
    print(f"\nTìm thấy {len(doc_files)} tài liệu:")
    for f in doc_files:
        print(f"  - {f.name}")

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
