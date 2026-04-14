"""
rag_answer.py — Sprint 2 + Sprint 3: Retrieval & Grounded Answer
================================================================
<<<<<<< HEAD
Sprint 2 (60 phút): Baseline RAG
  - Dense retrieval từ ChromaDB
  - Grounded answer function với prompt ép citation
  - Trả lời được ít nhất 3 câu hỏi mẫu, output có source

Sprint 3 (60 phút): Tuning tối thiểu
  - Thêm hybrid retrieval (dense + sparse/BM25)
  - Hoặc thêm rerank (cross-encoder)
  - Hoặc thử query transformation (expansion, decomposition, HyDE)
  - Tạo bảng so sánh baseline vs variant

Definition of Done Sprint 2:
  ✓ rag_answer("SLA ticket P1?") trả về câu trả lời có citation
  ✓ rag_answer("Câu hỏi không có trong docs") trả về "Không đủ dữ liệu"

Definition of Done Sprint 3:
  ✓ Có ít nhất 1 variant (hybrid / rerank / query transform) chạy được
  ✓ Giải thích được tại sao chọn biến đó để tune
"""

import os
from typing import List, Dict, Any, Optional, Tuple
=======
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
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
from dotenv import load_dotenv

load_dotenv()

<<<<<<< HEAD
# =============================================================================
# CẤU HÌNH
# =============================================================================

TOP_K_SEARCH = 10    # Số chunk lấy từ vector store trước rerank (search rộng)
TOP_K_SELECT = 3     # Số chunk gửi vào prompt sau rerank/select (top-3 sweet spot)

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")


# =============================================================================
# RETRIEVAL — DENSE (Vector Search)
=======
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
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
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
<<<<<<< HEAD
    
    chunks = []
    if results["documents"] and len(results["documents"]) > 0:
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        dists = results["distances"][0]
        for idx in range(len(docs)):
            chunks.append({
                "text": docs[idx],
                "metadata": metas[idx],
                "score": 1.0 - dists[idx]  # distance to similarity
            })
            
=======

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

>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
    return chunks


# =============================================================================
<<<<<<< HEAD
# RETRIEVAL — SPARSE / BM25 (Keyword Search)
# Dùng cho Sprint 3 Variant hoặc kết hợp Hybrid
=======
# RETRIEVAL — SPARSE / BM25
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
# =============================================================================

def retrieve_sparse(query: str, top_k: int = TOP_K_SEARCH) -> List[Dict[str, Any]]:
    """
    Sparse retrieval: tìm kiếm theo keyword (BM25).
    """
    import chromadb
<<<<<<< HEAD
    from index import CHROMA_DB_DIR
    # Try importing BM25
=======
    import re
    from index import CHROMA_DB_DIR

>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
    try:
        from rank_bm25 import BM25Okapi
    except ImportError:
        print("[retrieve_sparse] pip install rank-bm25 là cần thiết. Fallback về list rỗng.")
        return []

    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    collection = client.get_collection("rag_lab")
<<<<<<< HEAD
    
=======

>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
    results = collection.get(include=["documents", "metadatas"])
    if not results or not results["documents"]:
        return []

    all_chunks = []
    for i in range(len(results["documents"])):
        all_chunks.append({
            "text": results["documents"][i],
<<<<<<< HEAD
            "metadata": results["metadatas"][i]
        })
        
    corpus = [chunk["text"] for chunk in all_chunks]
    tokenized_corpus = [doc.lower().split() for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.lower().split()
    
    scores = bm25.get_scores(tokenized_query)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    
    top_chunks = []
    for idx in top_indices:
        chunk = all_chunks[idx].copy()
        chunk["score"] = scores[idx]
=======
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
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
        top_chunks.append(chunk)

    return top_chunks


# =============================================================================
<<<<<<< HEAD
# RETRIEVAL — HYBRID (Dense + Sparse với Reciprocal Rank Fusion)
=======
# RETRIEVAL — HYBRID (variant chính của Sprint 3)
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
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
<<<<<<< HEAD
    dense_results = retrieve_dense(query, top_k=top_k*2)
    sparse_results = retrieve_sparse(query, top_k=top_k*2)
    
    import hashlib
    def get_id(chunk):
        return hashlib.md5(chunk["text"].encode('utf-8')).hexdigest()
        
    rrf_scores = {}
    chunk_map = {}
    
    # Score Dense
=======
    dense_results = retrieve_dense(query, top_k=top_k * 2)
    sparse_results = retrieve_sparse(query, top_k=top_k * 2)

    import hashlib

    def get_id(chunk: Dict[str, Any]) -> str:
        return hashlib.md5(chunk["text"].encode("utf-8")).hexdigest()

    rrf_scores = {}
    chunk_map = {}

>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
    for rank, chunk in enumerate(dense_results):
        cid = get_id(chunk)
        chunk_map[cid] = chunk
        rrf_scores[cid] = rrf_scores.get(cid, 0.0) + dense_weight * (1.0 / (60.0 + rank + 1))
<<<<<<< HEAD
        
    # Score Sparse
=======

>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
    for rank, chunk in enumerate(sparse_results):
        cid = get_id(chunk)
        chunk_map[cid] = chunk
        rrf_scores[cid] = rrf_scores.get(cid, 0.0) + sparse_weight * (1.0 / (60.0 + rank + 1))
<<<<<<< HEAD
        
    ranked_cids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
    
=======

    ranked_cids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)

>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
    top_chunks = []
    for cid in ranked_cids[:top_k]:
        chunk = chunk_map[cid].copy()
        chunk["score"] = rrf_scores[cid]
        top_chunks.append(chunk)
<<<<<<< HEAD
        
=======

>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
    return top_chunks


# =============================================================================
<<<<<<< HEAD
# RERANK (Sprint 3 alternative)
# Cross-encoder để chấm lại relevance sau search rộng
# =============================================================================

def rerank(
    query: str,
    candidates: List[Dict[str, Any]],
    top_k: int = TOP_K_SELECT,
) -> List[Dict[str, Any]]:
    """
    Rerank các candidate chunks bằng cross-encoder.

    Cross-encoder: chấm lại "chunk nào thực sự trả lời câu hỏi này?"
    MMR (Maximal Marginal Relevance): giữ relevance nhưng giảm trùng lặp

    Funnel logic (từ slide):
      Search rộng (top-20) → Rerank (top-6) → Select (top-3)

    TODO Sprint 3 (nếu chọn rerank):
    Option A — Cross-encoder:
        from sentence_transformers import CrossEncoder
        model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        pairs = [[query, chunk["text"]] for chunk in candidates]
        scores = model.predict(pairs)
        ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in ranked[:top_k]]

    Option B — Rerank bằng LLM (đơn giản hơn nhưng tốn token):
        Gửi list chunks cho LLM, yêu cầu chọn top_k relevant nhất

    Khi nào dùng rerank:
    - Dense/hybrid trả về nhiều chunk nhưng có noise
    - Muốn chắc chắn chỉ 3-5 chunk tốt nhất vào prompt
    """
    # TODO Sprint 3: Implement rerank
    # Tạm thời trả về top_k đầu tiên (không rerank)
    return candidates[:top_k]


# =============================================================================
# QUERY TRANSFORMATION (Sprint 3 alternative)
# =============================================================================

def transform_query(query: str, strategy: str = "expansion") -> List[str]:
    """
    Biến đổi query để tăng recall.

    Strategies:
      - "expansion": Thêm từ đồng nghĩa, alias, tên cũ
      - "decomposition": Tách query phức tạp thành 2-3 sub-queries
      - "hyde": Sinh câu trả lời giả (hypothetical document) để embed thay query

    TODO Sprint 3 (nếu chọn query transformation):
    Gọi LLM với prompt phù hợp với từng strategy.

    Ví dụ expansion prompt:
        "Given the query: '{query}'
         Generate 2-3 alternative phrasings or related terms in Vietnamese.
         Output as JSON array of strings."

    Ví dụ decomposition:
        "Break down this complex query into 2-3 simpler sub-queries: '{query}'
         Output as JSON array."

    Khi nào dùng:
    - Expansion: query dùng alias/tên cũ (ví dụ: "Approval Matrix" → "Access Control SOP")
    - Decomposition: query hỏi nhiều thứ một lúc
    - HyDE: query mơ hồ, search theo nghĩa không hiệu quả
    """
    # TODO Sprint 3: Implement query transformation
    # Tạm thời trả về query gốc
=======
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
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
    return [query]


# =============================================================================
<<<<<<< HEAD
# GENERATION — GROUNDED ANSWER FUNCTION
=======
# GENERATION
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
# =============================================================================

def build_context_block(chunks: List[Dict[str, Any]]) -> str:
    """
<<<<<<< HEAD
    Đóng gói danh sách chunks thành context block để đưa vào prompt.

    Format: structured snippets với source, section, score (từ slide).
    Mỗi chunk có số thứ tự [1], [2], ... để model dễ trích dẫn.
=======
    Đóng gói chunks thành context block với source, section, score.
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
    """
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk.get("metadata", {})
        source = meta.get("source", "unknown")
        section = meta.get("section", "")
        score = chunk.get("score", 0)
        text = chunk.get("text", "")

<<<<<<< HEAD
        # TODO: Tùy chỉnh format nếu muốn (thêm effective_date, department, ...)
        header = f"[{i}] {source}"
        if section:
            header += f" | {section}"
        if score > 0:
=======
        header = f"[{i}] {source}"
        if section:
            header += f" | {section}"
        if score is not None:
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
            header += f" | score={score:.2f}"

        context_parts.append(f"{header}\n{text}")

    return "\n\n".join(context_parts)


def build_grounded_prompt(query: str, context_block: str) -> str:
    """
<<<<<<< HEAD
    Xây dựng grounded prompt theo 4 quy tắc từ slide:
    1. Evidence-only: Chỉ trả lời từ retrieved context
    2. Abstain: Thiếu context thì nói không đủ dữ liệu
    3. Citation: Gắn source/section khi có thể
    4. Short, clear, stable: Output ngắn, rõ, nhất quán

    TODO Sprint 2:
    Đây là prompt baseline. Trong Sprint 3, bạn có thể:
    - Thêm hướng dẫn về format output (JSON, bullet points)
    - Thêm ngôn ngữ phản hồi (tiếng Việt vs tiếng Anh)
    - Điều chỉnh tone phù hợp với use case (CS helpdesk, IT support)
    """
    prompt = f"""Answer only from the retrieved context below.
If the context is insufficient to answer the question, say you do not know and do not make up information.
Cite the source field (in brackets like [1]) when possible.
Keep your answer short, clear, and factual.
=======
    Prompt grounding: chỉ trả lời từ context, nếu thiếu thì abstain.
    """
    prompt = f"""Answer only from the retrieved context below.
If the context is insufficient, respond exactly: Không đủ dữ liệu.
Do not make up any facts.
Use citations like [1], [2] when stating factual claims.
Keep the answer short, clear, and factual.
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
Respond in the same language as the question.

Question: {query}

Context:
{context_block}

Answer:"""
    return prompt


def call_llm(prompt: str) -> str:
    """
<<<<<<< HEAD
    Gọi LLM để sinh câu trả lời.
    Sử dụng OpenAI API.
    """
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
=======
    Gọi LLM bằng OpenAI API, dùng client global để tránh khởi tạo lặp lại.
    """
    response = _OPENAI_CLIENT.chat.completions.create(
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=512,
    )
<<<<<<< HEAD
    return response.choices[0].message.content
=======
    return response.choices[0].message.content.strip()
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba


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
<<<<<<< HEAD

    Args:
        query: Câu hỏi
        retrieval_mode: "dense" | "sparse" | "hybrid"
        top_k_search: Số chunk lấy từ vector store (search rộng)
        top_k_select: Số chunk đưa vào prompt (sau rerank/select)
        use_rerank: Có dùng cross-encoder rerank không
        verbose: In thêm thông tin debug

    Returns:
        Dict với:
          - "answer": câu trả lời grounded
          - "sources": list source names trích dẫn
          - "chunks_used": list chunks đã dùng
          - "query": query gốc
          - "config": cấu hình pipeline đã dùng

    TODO Sprint 2 — Implement pipeline cơ bản:
    1. Chọn retrieval function dựa theo retrieval_mode
    2. Gọi rerank() nếu use_rerank=True
    3. Truncate về top_k_select chunks
    4. Build context block và grounded prompt
    5. Gọi call_llm() để sinh câu trả lời
    6. Trả về kết quả kèm metadata

    TODO Sprint 3 — Thử các variant:
    - Variant A: đổi retrieval_mode="hybrid"
    - Variant B: bật use_rerank=True
    - Variant C: thêm query transformation trước khi retrieve
=======
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
    """
    config = {
        "retrieval_mode": retrieval_mode,
        "top_k_search": top_k_search,
        "top_k_select": top_k_select,
        "use_rerank": use_rerank,
    }

<<<<<<< HEAD
    # --- Bước 1: Retrieve ---
=======
    # --- Retrieve ---
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
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
<<<<<<< HEAD
        for i, c in enumerate(candidates[:3]):
            print(f"  [{i+1}] score={c.get('score', 0):.3f} | {c['metadata'].get('source', '?')}")

    # --- Bước 2: Rerank (optional) ---
=======
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
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
    if use_rerank:
        candidates = rerank(query, candidates, top_k=top_k_select)
    else:
        candidates = candidates[:top_k_select]

    if verbose:
        print(f"[RAG] After select: {len(candidates)} chunks")

<<<<<<< HEAD
    # --- Bước 3: Build context và prompt ---
=======
    # --- Build context + prompt ---
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
    context_block = build_context_block(candidates)
    prompt = build_grounded_prompt(query, context_block)

    if verbose:
<<<<<<< HEAD
        print(f"\n[RAG] Prompt:\n{prompt[:500]}...\n")

    # --- Bước 4: Generate ---
    answer = call_llm(prompt)

    # --- Bước 5: Extract sources ---
    sources = list({
        c["metadata"].get("source", "unknown")
        for c in candidates
    })
=======
        print(f"\n[RAG] Prompt:\n{prompt[:700]}...\n")

    # --- Generate ---
    answer = call_llm(prompt)

    # --- Extract sources ---
    sources = list({c["metadata"].get("source", "unknown") for c in candidates})
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba

    return {
        "query": query,
        "answer": answer,
        "sources": sources,
        "chunks_used": candidates,
        "config": config,
<<<<<<< HEAD
=======
        "abstained": False,
        "abstain_reason": None,
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
    }


# =============================================================================
<<<<<<< HEAD
# SPRINT 3: SO SÁNH BASELINE VS VARIANT
=======
# COMPARE BASELINE VS VARIANT
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
# =============================================================================

def compare_retrieval_strategies(query: str) -> None:
    """
<<<<<<< HEAD
    So sánh các retrieval strategies với cùng một query.

    TODO Sprint 3:
    Chạy hàm này để thấy sự khác biệt giữa dense, sparse, hybrid.
    Dùng để justify tại sao chọn variant đó cho Sprint 3.

    A/B Rule (từ slide): Chỉ đổi MỘT biến mỗi lần.
    """
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print('='*60)

    strategies = ["dense", "hybrid"]  # Thêm "sparse" sau khi implement
=======
    So sánh dense vs hybrid và in retrieval evidence rõ ràng.
    """
    print(f"\n{'='*70}")
    print(f"Query: {query}")
    print(f"{'='*70}")

    strategies = ["dense", PRIMARY_VARIANT]
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba

    for strategy in strategies:
        print(f"\n--- Strategy: {strategy} ---")
        try:
<<<<<<< HEAD
            result = rag_answer(query, retrieval_mode=strategy, verbose=False)
            print(f"Answer: {result['answer']}")
            print(f"Sources: {result['sources']}")
        except NotImplementedError as e:
            print(f"Chưa implement: {e}")
=======
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

>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
        except Exception as e:
            print(f"Lỗi: {e}")


# =============================================================================
<<<<<<< HEAD
# MAIN — Demo và Test
=======
# MAIN
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Sprint 2 + 3: RAG Answer Pipeline")
    print("=" * 60)

<<<<<<< HEAD
    # Test queries từ data/test_questions.json
=======
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
    test_queries = [
        "SLA xử lý ticket P1 là bao lâu?",
        "Khách hàng có thể yêu cầu hoàn tiền trong bao nhiêu ngày?",
        "Ai phải phê duyệt để cấp quyền Level 3?",
<<<<<<< HEAD
        "ERR-403-AUTH là lỗi gì?",  # Query không có trong docs → kiểm tra abstain
=======
        "ERR-403-AUTH là lỗi gì?",
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
    ]

    print("\n--- Sprint 2: Test Baseline (Dense) ---")
    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            result = rag_answer(query, retrieval_mode="dense", verbose=True)
            print(f"Answer: {result['answer']}")
            print(f"Sources: {result['sources']}")
<<<<<<< HEAD
        except NotImplementedError:
            print("Chưa implement — hoàn thành TODO trong retrieve_dense() và call_llm() trước.")
        except Exception as e:
            print(f"Lỗi: {e}")

    # Sprint 3: So sánh strategies
    print("\n--- Sprint 3: So sánh strategies ---")
=======
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
>>>>>>> 0087ec5e822ab33fb34176e109a5daf1d07e4eba
    compare_retrieval_strategies("Approval Matrix để cấp quyền là tài liệu nào?")
    compare_retrieval_strategies("ERR-403-AUTH")

    print("\nHoàn tất Sprint 2 & 3")
