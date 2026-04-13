"""
rag_answer.py — Sprint 2 + Sprint 3: Retrieval & Grounded Answer
================================================================
Sprint 2:
  - Dense retrieval từ ChromaDB
  - Grounded answer function với prompt ép citation
  - Trả lời được câu hỏi mẫu, output có source

Sprint 3:
  - Variant chính: hybrid retrieval (dense + sparse/BM25)
  - So sánh baseline vs hybrid
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

TOP_K_SEARCH = 10
TOP_K_SELECT = 3
ABSTAIN_MIN_SCORE_DENSE = 0.22
ABSTAIN_MIN_SCORE_HYBRID = 0.01
PRIMARY_VARIANT = "hybrid"

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

from openai import OpenAI
_OPENAI_CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =============================================================================
# RETRIEVAL — DENSE
# =============================================================================

def retrieve_dense(query: str, top_k: int = TOP_K_SEARCH) -> List[Dict[str, Any]]:
    """
    Dense retrieval: tìm kiếm theo embedding similarity trong ChromaDB.
    """
    import chromadb
    from index import get_embedding, CHROMA_DB_DIR

    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    collection = client.get_collection("rag_lab")

    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    if results.get("documents") and len(results["documents"]) > 0:
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        dists = results["distances"][0]

        for idx in range(len(docs)):
            dist = dists[idx]
            score = 1.0 - dist if dist is not None else 0.0
            chunks.append({
                "text": docs[idx],
                "metadata": metas[idx],
                "score": score,
            })

    return chunks


# =============================================================================
# RETRIEVAL — SPARSE / BM25
# =============================================================================

def retrieve_sparse(query: str, top_k: int = TOP_K_SEARCH) -> List[Dict[str, Any]]:
    """
    Sparse retrieval: tìm kiếm theo keyword (BM25).
    """
    import chromadb
    import re
    from index import CHROMA_DB_DIR

    try:
        from rank_bm25 import BM25Okapi
    except ImportError:
        print("[retrieve_sparse] pip install rank-bm25 là cần thiết. Fallback về list rỗng.")
        return []

    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    collection = client.get_collection("rag_lab")

    results = collection.get(include=["documents", "metadatas"])
    if not results or not results["documents"]:
        return []

    all_chunks = []
    for i in range(len(results["documents"])):
        all_chunks.append({
            "text": results["documents"][i],
            "metadata": results["metadatas"][i],
        })

    def tokenize(text: str) -> List[str]:
        return re.findall(r"[\w\-]+", text.lower())

    corpus = [chunk["text"] for chunk in all_chunks]
    tokenized_corpus = [tokenize(doc) for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = tokenize(query)

    scores = bm25.get_scores(tokenized_query)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

    top_chunks = []
    for idx in top_indices:
        chunk = all_chunks[idx].copy()
        chunk["score"] = float(scores[idx])
        top_chunks.append(chunk)

    return top_chunks


# =============================================================================
# RETRIEVAL — HYBRID (variant chính của Sprint 3)
# =============================================================================

def retrieve_hybrid(
    query: str,
    top_k: int = TOP_K_SEARCH,
    dense_weight: float = 0.6,
    sparse_weight: float = 0.4,
) -> List[Dict[str, Any]]:
    """
    Hybrid retrieval: kết hợp dense và sparse bằng Reciprocal Rank Fusion (RRF).
    """
    dense_results = retrieve_dense(query, top_k=top_k * 2)
    sparse_results = retrieve_sparse(query, top_k=top_k * 2)

    import hashlib

    def get_id(chunk: Dict[str, Any]) -> str:
        return hashlib.md5(chunk["text"].encode("utf-8")).hexdigest()

    rrf_scores = {}
    chunk_map = {}

    for rank, chunk in enumerate(dense_results):
        cid = get_id(chunk)
        chunk_map[cid] = chunk
        rrf_scores[cid] = rrf_scores.get(cid, 0.0) + dense_weight * (1.0 / (60.0 + rank + 1))

    for rank, chunk in enumerate(sparse_results):
        cid = get_id(chunk)
        chunk_map[cid] = chunk
        rrf_scores[cid] = rrf_scores.get(cid, 0.0) + sparse_weight * (1.0 / (60.0 + rank + 1))

    ranked_cids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)

    top_chunks = []
    for cid in ranked_cids[:top_k]:
        chunk = chunk_map[cid].copy()
        chunk["score"] = rrf_scores[cid]
        top_chunks.append(chunk)

    return top_chunks


# =============================================================================
# RERANK / QUERY TRANSFORM (placeholder)
# =============================================================================

def rerank(query: str, candidates: List[Dict[str, Any]], top_k: int = TOP_K_SELECT) -> List[Dict[str, Any]]:
    """
    Placeholder: chưa implement cross-encoder thật.
    """
    return candidates[:top_k]


def transform_query(query: str, strategy: str = "expansion") -> List[str]:
    """
    Placeholder: chưa implement thật.
    """
    return [query]


# =============================================================================
# GENERATION
# =============================================================================

def build_context_block(chunks: List[Dict[str, Any]]) -> str:
    """
    Đóng gói chunks thành context block với source, section, score.
    """
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk.get("metadata", {})
        source = meta.get("source", "unknown")
        section = meta.get("section", "")
        score = chunk.get("score", 0)
        text = chunk.get("text", "")

        header = f"[{i}] {source}"
        if section:
            header += f" | {section}"
        if score is not None:
            header += f" | score={score:.2f}"

        context_parts.append(f"{header}\n{text}")

    return "\n\n".join(context_parts)


def build_grounded_prompt(query: str, context_block: str) -> str:
    """
    Prompt grounding: chỉ trả lời từ context, nếu thiếu thì abstain.
    """
    prompt = f"""Answer only from the retrieved context below.
If the context is insufficient, respond exactly: Không đủ dữ liệu.
Do not make up any facts.
Use citations like [1], [2] when stating factual claims.
Keep the answer short, clear, and factual.
Respond in the same language as the question.

Question: {query}

Context:
{context_block}

Answer:"""
    return prompt


def call_llm(prompt: str) -> str:
    """
    Gọi LLM bằng OpenAI API, dùng client global để tránh khởi tạo lặp lại.
    """
    response = _OPENAI_CLIENT.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=512,
    )
    return response.choices[0].message.content.strip()


def rag_answer(
    query: str,
    retrieval_mode: str = "dense",
    top_k_search: int = TOP_K_SEARCH,
    top_k_select: int = TOP_K_SELECT,
    use_rerank: bool = False,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Pipeline RAG hoàn chỉnh: query → retrieve → (rerank) → generate.
    """
    config = {
        "retrieval_mode": retrieval_mode,
        "top_k_search": top_k_search,
        "top_k_select": top_k_select,
        "use_rerank": use_rerank,
    }

    # --- Retrieve ---
    if retrieval_mode == "dense":
        candidates = retrieve_dense(query, top_k=top_k_search)
    elif retrieval_mode == "sparse":
        candidates = retrieve_sparse(query, top_k=top_k_search)
    elif retrieval_mode == "hybrid":
        candidates = retrieve_hybrid(query, top_k=top_k_search)
    else:
        raise ValueError(f"retrieval_mode không hợp lệ: {retrieval_mode}")

    if verbose:
        print(f"\n[RAG] Query: {query}")
        print(f"[RAG] Retrieved {len(candidates)} candidates (mode={retrieval_mode})")
        for i, c in enumerate(candidates[:5], 1):
            print(
                f"  [{i}] score={c.get('score', 0):.3f} | "
                f"{c['metadata'].get('source', '?')} | "
                f"{c['metadata'].get('section', '')}"
            )

    # --- Abstain sớm nếu không có evidence ---
    if not candidates:
        return {
            "query": query,
            "answer": "Không đủ dữ liệu.",
            "sources": [],
            "chunks_used": [],
            "config": config,
            "abstained": True,
            "abstain_reason": "no_candidates",
        }

    top_score = candidates[0].get("score", 0) or 0.0

    if retrieval_mode == "dense" and top_score < ABSTAIN_MIN_SCORE_DENSE:
        return {
            "query": query,
            "answer": "Không đủ dữ liệu.",
            "sources": [],
            "chunks_used": candidates[:top_k_select],
            "config": config,
            "abstained": True,
            "abstain_reason": f"low_dense_score<{ABSTAIN_MIN_SCORE_DENSE}",
        }

    if retrieval_mode == "hybrid" and top_score < ABSTAIN_MIN_SCORE_HYBRID:
        return {
            "query": query,
            "answer": "Không đủ dữ liệu.",
            "sources": [],
            "chunks_used": candidates[:top_k_select],
            "config": config,
            "abstained": True,
            "abstain_reason": f"low_hybrid_score<{ABSTAIN_MIN_SCORE_HYBRID}",
        }

    # --- Rerank/select ---
    if use_rerank:
        candidates = rerank(query, candidates, top_k=top_k_select)
    else:
        candidates = candidates[:top_k_select]

    if verbose:
        print(f"[RAG] After select: {len(candidates)} chunks")

    # --- Build context + prompt ---
    context_block = build_context_block(candidates)
    prompt = build_grounded_prompt(query, context_block)

    if verbose:
        print(f"\n[RAG] Prompt:\n{prompt[:700]}...\n")

    # --- Generate ---
    answer = call_llm(prompt)

    # --- Extract sources ---
    sources = list({c["metadata"].get("source", "unknown") for c in candidates})

    return {
        "query": query,
        "answer": answer,
        "sources": sources,
        "chunks_used": candidates,
        "config": config,
        "abstained": False,
        "abstain_reason": None,
    }


# =============================================================================
# COMPARE BASELINE VS VARIANT
# =============================================================================

def compare_retrieval_strategies(query: str) -> None:
    """
    So sánh dense vs hybrid và in retrieval evidence rõ ràng.
    """
    print(f"\n{'='*70}")
    print(f"Query: {query}")
    print(f"{'='*70}")

    strategies = ["dense", PRIMARY_VARIANT]

    for strategy in strategies:
        print(f"\n--- Strategy: {strategy} ---")
        try:
            result = rag_answer(
                query,
                retrieval_mode=strategy,
                top_k_search=TOP_K_SEARCH,
                top_k_select=TOP_K_SELECT,
                use_rerank=False,
                verbose=False,
            )

            print(f"Abstained: {result.get('abstained')}")
            print(f"Answer: {result['answer']}")
            print(f"Sources: {result['sources']}")

            chunks = result.get("chunks_used", [])
            if not chunks:
                print("No chunks used.")
                continue

            print("Top evidence used:")
            for i, chunk in enumerate(chunks, 1):
                meta = chunk.get("metadata", {})
                print(
                    f"  [{i}] score={chunk.get('score', 0):.3f} | "
                    f"source={meta.get('source', '?')} | "
                    f"section={meta.get('section', '')}"
                )
                preview = chunk.get("text", "").replace("\n", " ")[:180]
                print(f"      {preview}...")

        except Exception as e:
            print(f"Lỗi: {e}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Sprint 2 + 3: RAG Answer Pipeline")
    print("=" * 60)

    test_queries = [
        "SLA xử lý ticket P1 là bao lâu?",
        "Khách hàng có thể yêu cầu hoàn tiền trong bao nhiêu ngày?",
        "Ai phải phê duyệt để cấp quyền Level 3?",
        "ERR-403-AUTH là lỗi gì?",
    ]

    print("\n--- Sprint 2: Test Baseline (Dense) ---")
    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            result = rag_answer(query, retrieval_mode="dense", verbose=True)
            print(f"Answer: {result['answer']}")
            print(f"Sources: {result['sources']}")
            print(f"Abstained: {result.get('abstained')}")
        except Exception as e:
            print(f"Lỗi: {e}")

    print(f"\n--- Sprint 3: Variant chính = {PRIMARY_VARIANT} ---")
    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            result = rag_answer(query, retrieval_mode=PRIMARY_VARIANT, verbose=True)
            print(f"Answer: {result['answer']}")
            print(f"Sources: {result['sources']}")
            print(f"Abstained: {result.get('abstained')}")
        except Exception as e:
            print(f"Lỗi: {e}")

    print("\n--- Sprint 3: So sánh baseline vs hybrid ---")
    compare_retrieval_strategies("Approval Matrix để cấp quyền là tài liệu nào?")
    compare_retrieval_strategies("ERR-403-AUTH")

    print("\nHoàn tất Sprint 2 & 3")
