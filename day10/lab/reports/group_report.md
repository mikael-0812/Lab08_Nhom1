# BÃ¡o CÃ¡o NhÃ³m â€” Lab Day 10: Data Pipeline & Data Observability

**TÃªn nhÃ³m:** NhÃ³m Day 10  
**ThÃ nh viÃªn:**
| TÃªn | Vai trÃ² (Day 10) | Email |
|-----|------------------|-------|
| ÄÃ o Quang Tháº¯ng | **Ingestion Owner** + **Monitoring / Docs Owner** |  |
| Pháº¡m Háº£i ÄÄƒng | **Embed Owner** (Chroma collection, idempotency, eval) |  |
| Pháº¡m HoÃ ng Kim LiÃªn | **Cleaning / Quality Owner** (cleaning_rules.py, expectations.py, quarantine) |  |

**NgÃ y ná»™p:** 2026-04-15  
**Repo:** Lecture-Day-08-09-10-main  
**Äá»™ dÃ i khuyáº¿n nghá»‹:** 600â€“1000 tá»«

---

> **Ná»™p táº¡i:** `reports/group_report.md`  
> **Deadline commit:** xem `SCORING.md` (code/trace sá»›m; report cÃ³ thá»ƒ muá»™n hÆ¡n náº¿u Ä‘Æ°á»£c phÃ©p).  
> Pháº£i cÃ³ **run_id**, **Ä‘Æ°á»ng dáº«n artifact**, vÃ  **báº±ng chá»©ng before/after** (CSV eval hoáº·c screenshot).

---

## 1. Pipeline tá»•ng quan (150â€“200 tá»«)

Nguá»“n raw lÃ  file CSV máº«u `data/raw/policy_export_dirty.csv` â€” mÃ´ phá»ng export tá»« há»‡ thá»‘ng CRM/HR ná»™i bá»™ vá»›i 10 dÃ²ng chá»©a nhiá»u loáº¡i lá»—i: duplicate chunk, doc_id ngoÃ i allowlist (`legacy_catalog_xyz_zzz`), ngÃ y khÃ´ng ISO (`01/02/2026`), chunk rá»—ng, HR policy cÅ© (2025, "10 ngÃ y phÃ©p nÄƒm"), vÃ  stale refund window ("14 ngÃ y" tá»« policy v3).

Pipeline cháº¡y end-to-end qua 4 bÆ°á»›c: **ingest** (Ä‘á»c CSV raw) â†’ **clean** (Ã¡p dá»¥ng 9 cleaning rules) â†’ **validate** (cháº¡y 8 expectations) â†’ **embed** (upsert vÃ o ChromaDB collection `day10_kb` + prune stale vectors). Má»—i run táº¡o `run_id` ghi trong log + manifest JSON Ä‘á»ƒ truy váº¿t.

**TÃ³m táº¯t luá»“ng:**

raw CSV â†’ `load_raw_csv()` â†’ `clean_rows()` â†’ cleaned CSV + quarantine CSV â†’ `run_expectations()` â†’ halt/pass â†’ `cmd_embed_internal()` (upsert + prune) â†’ manifest + freshness check

**Lá»‡nh cháº¡y má»™t dÃ²ng:**

```bash
$env:PYTHONIOENCODING="utf-8"; py etl_pipeline.py run --run-id final-clean
```

`run_id` Ä‘Æ°á»£c ghi á»Ÿ dÃ²ng Ä‘áº§u log: `run_id=final-clean` vÃ  trong `artifacts/manifests/manifest_final-clean.json`.

---

## 2. Cleaning & expectation (150â€“200 tá»«)

Baseline Ä‘Ã£ cÃ³ 6 rule (allowlist doc_id, parse ngÃ y ISO/DMY, quarantine HR cÅ©, fix refund 14â†’7, dedupe, loáº¡i chunk rá»—ng) vÃ  6 expectation (min_one_row, no_empty_doc_id, refund_no_stale_14d_window, chunk_min_length_8, effective_date_iso, hr_leave_no_stale_10d_annual).

TÃ´i thÃªm **3 rule má»›i** vÃ  **2 expectation má»›i**:

### 2a. Báº£ng metric_impact (báº¯t buá»™c â€” chá»‘ng trivial)

| Rule / Expectation má»›i (tÃªn ngáº¯n) | TrÆ°á»›c (sá»‘ liá»‡u) | Sau / khi inject (sá»‘ liá»‡u) | Chá»©ng cá»© (log / CSV / commit) |
|-----------------------------------|------------------|-----------------------------|-------------------------------|
| R1: BOM/zero-width strip | Náº¿u inject BOM: chunk_text chá»©a `\ufeff` | Sau clean: BOM bá»‹ loáº¡i, text sáº¡ch | `cleaning_rules.py` â€” Pháº¡m HoÃ ng Kim LiÃªn |
| R2: Whitespace normalize | chunk cÃ³ multi-space/tab: dedupe miss | Sau normalize: collapse â†’ dedupe chÃ­nh xÃ¡c hÆ¡n | `cleaning_rules.py` â€” Pháº¡m HoÃ ng Kim LiÃªn |
| R3: Minimum meaningful content (â‰¤10 alphanum) | chunk gáº§n-rá»—ng lá»t qua "missing_chunk_text" | quarantine thÃªm dÃ²ng `insufficient_meaningful_content` | `cleaning_rules.py` â€” Pháº¡m HoÃ ng Kim LiÃªn |
| E7: unique_chunk_id (halt) | Náº¿u inject duplicate chunk_id: upsert máº¥t data | halt pipeline, `duplicate_chunk_ids>0` | `expectations.py` â€” Pháº¡m HoÃ ng Kim LiÃªn |
| E8: no_bom_zero_width_chars (warn) | Sau inject BOM váº«n cÃ²n trong cleaned | warn, `rows_with_bom>0` | `expectations.py` â€” Pháº¡m HoÃ ng Kim LiÃªn |

**Rule chÃ­nh (baseline + má»Ÿ rá»™ng):**

- Baseline: allowlist doc_id, parse DD/MM/YYYYâ†’ISO, quarantine HR<2026, fix refund 14â†’7, dedupe text, loáº¡i chunk rá»—ng
- Má»›i: BOM strip (R1), whitespace normalize (R2), minimum content filter (R3)

**VÃ­ dá»¥ 1 láº§n expectation fail vÃ  cÃ¡ch xá»­ lÃ½:**

Khi cháº¡y `--no-refund-fix --skip-validate`: expectation `refund_no_stale_14d_window` **FAIL** (violations=1). Pipeline warn nhÆ°ng váº«n embed vÃ¬ `--skip-validate`. Eval sau Ä‘Ã³ cho tháº¥y `hits_forbidden=yes` cho cÃ¢u refund. Cháº¡y láº¡i pipeline chuáº©n â†’ expectation OK â†’ `hits_forbidden=no`.

---

## 3. Before / after áº£nh hÆ°á»Ÿng retrieval hoáº·c agent (200â€“250 tá»«)

**Ká»‹ch báº£n inject:** Sprint 3 â€” cháº¡y `py etl_pipeline.py run --run-id inject-bad --no-refund-fix --skip-validate` Ä‘á»ƒ cá»‘ Ã½ embed chunk stale "14 ngÃ y lÃ m viá»‡c" vÃ o ChromaDB.

**Káº¿t quáº£ Ä‘á»‹nh lÆ°á»£ng:**

| CÃ¢u há»i | Metric | inject-bad (before) | final-clean (after) |
|---------|--------|---------------------|---------------------|
| `q_refund_window` | `contains_expected` | yes | yes |
| `q_refund_window` | `hits_forbidden` | **yes** âŒ | **no** âœ… |
| `q_leave_version` | `contains_expected` | yes | yes |
| `q_leave_version` | `hits_forbidden` | no | no |
| `q_leave_version` | `top1_doc_expected` | yes | yes |
| `q_p1_sla` | `contains_expected` | yes | yes |
| `q_lockout` | `contains_expected` | yes | yes |

**PhÃ¢n tÃ­ch:** Khi inject (táº¯t fix refund), chunk "14 ngÃ y lÃ m viá»‡c" lá»t vÃ o top-k retrieval â†’ `hits_forbidden=yes`. Agent sáº½ trÃ­ch dáº«n thÃ´ng tin sai. Sau khi cháº¡y pipeline chuáº©n: rule fix 14â†’7 hoáº¡t Ä‘á»™ng, embed prune xÃ³a vector stale (`embed_prune_removed=1`), eval trá»Ÿ láº¡i sáº¡ch.

CÃ¢u `q_leave_version` á»•n Ä‘á»‹nh á»Ÿ cáº£ 2 ká»‹ch báº£n vÃ¬ rule quarantine HR cÅ© luÃ´n báº­t (khÃ´ng bá»‹ táº¯t bá»Ÿi `--no-refund-fix`), chá»©ng minh cleaning rule versioning hoáº¡t Ä‘á»™ng hiá»‡u quáº£.

Artifact: `artifacts/eval/after_inject_bad.csv`, `artifacts/eval/before_after_eval.csv`

---

## 4. Freshness & monitoring (100â€“150 tá»«)

**SLA chá»n:** 24 giá» (`FRESHNESS_SLA_HOURS=24` trong `.env`). Ã nghÄ©a: corpus pháº£i Ä‘Æ°á»£c cáº­p nháº­t trong vÃ²ng 24h ká»ƒ tá»« láº§n export cuá»‘i.

**Káº¿t quáº£:** `freshness_check=FAIL` â€” `age_hours=118.5`, vÆ°á»£t SLA 24h.

ÄÃ¢y lÃ  **FAIL há»£p lÃ½ trÃªn data máº«u**: CSV máº«u cÃ³ `exported_at=2026-04-10T08:00:00` (cÃ¡ch hiá»‡n táº¡i ~5 ngÃ y). Trong production, pipeline cháº¡y hÃ ng ngÃ y vá»›i export má»›i â†’ sáº½ PASS.

Freshness Ä‘o táº¡i boundary `publish` (sau embed) â€” Ä‘á»c `latest_exported_at` tá»« manifest. Náº¿u cáº§n Ä‘o 2 boundary (ingest + publish), cáº§n thÃªm timestamp vÃ o log á»Ÿ bÆ°á»›c ingest.

---

## 5. LiÃªn há»‡ Day 09 (50â€“100 tá»«)

Pipeline Day 10 xá»­ lÃ½ cÃ¹ng domain tÃ i liá»‡u vá»›i Day 09 (policy_refund_v4, sla_p1_2026, it_helpdesk_faq, hr_leave_policy). Tuy nhiÃªn, **tÃ¡ch collection** `day10_kb` Ä‘á»ƒ trÃ¡nh xung Ä‘á»™t khi thÃ­ nghiá»‡m inject/clean. Náº¿u cáº§n tÃ­ch há»£p, Ä‘á»•i `CHROMA_COLLECTION` trong `.env` hoáº·c export cleaned CSV sang `day09/lab/data/docs/`.

---

## 6. Rá»§i ro cÃ²n láº¡i & viá»‡c chÆ°a lÃ m

- Bá»™ dá»¯ liá»‡u chá»‰ 10 rows â€” chÆ°a Ä‘á»§ cho distribution monitoring cÃ³ Ã½ nghÄ©a thá»‘ng kÃª.
- Freshness chá»‰ Ä‘o 1 boundary (publish), chÆ°a tÃ¡ch ingest boundary.
- ChÆ°a cÃ³ LLM-judge eval end-to-end.
- Encoding Windows (cp1252) cáº§n workaround `PYTHONIOENCODING=utf-8`.
- ChÆ°a tÃ­ch há»£p scheduler/cron tá»± Ä‘á»™ng.

