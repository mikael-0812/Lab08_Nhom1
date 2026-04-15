# BÃ¡o CÃ¡o CÃ¡ NhÃ¢n â€” Lab Day 10: Data Pipeline & Observability

**Há» vÃ  tÃªn:** ÄÃ o Quang Tháº¯ng  
**Vai trÃ²:** Ingestion Owner + Monitoring / Docs Owner  
**NgÃ y ná»™p:** 2026-04-15  
**Äá»™ dÃ i yÃªu cáº§u:** **400â€“650 tá»«**

---

## 1. TÃ´i phá»¥ trÃ¡ch pháº§n nÃ o? (80â€“120 tá»«)

**File / module:**

- `etl_pipeline.py` â€” pháº§n `load_raw_csv()`, `cmd_run()` (logging `raw_records`, `cleaned_records`, `quarantine_records`), táº¡o `manifest_<run_id>.json`
- `data/raw/policy_export_dirty.csv` â€” Ä‘á»‹nh nghÄ©a raw path Ä‘áº§u vÃ o
- `monitoring/freshness_check.py` â€” Ä‘á»c manifest, tÃ­nh `age_hours`, so sÃ¡nh SLA
- `docs/pipeline_architecture.md` â€” sÆ¡ Ä‘á»“ Mermaid + báº£ng trÃ¡ch nhiá»‡m
- `docs/data_contract.md` â€” source map (â‰¥2 nguá»“n) + schema + quarantine rules
- `docs/runbook.md` â€” 5 má»¥c Symptom â†’ Prevention
- `docs/quality_report.md` â€” sá»‘ liá»‡u thá»±c + before/after evidence
- `reports/group_report.md` â€” bÃ¡o cÃ¡o nhÃ³m

**Káº¿t ná»‘i vá»›i thÃ nh viÃªn khÃ¡c:** Sau khi tÃ´i ingest raw â†’ Pháº¡m HoÃ ng Kim LiÃªn clean + validate â†’ Pháº¡m Háº£i ÄÄƒng embed â†’ tÃ´i láº¥y manifest Ä‘á»ƒ check freshness.

**Báº±ng chá»©ng:** log `run_id=final-clean` trong `artifacts/logs/run_final-clean.log`, manifest `artifacts/manifests/manifest_final-clean.json`.

---

## 2. Má»™t quyáº¿t Ä‘á»‹nh ká»¹ thuáº­t (100â€“150 tá»«)

**Quyáº¿t Ä‘á»‹nh:** Thiáº¿t káº¿ `run_id` lÃ  timestamp UTC (`2026-04-15T08-11Z`) thay vÃ¬ sá»‘ tÄƒng dáº§n.

**Bá»‘i cáº£nh:** Pipeline cháº¡y nhiá»u láº§n (chuáº©n, inject, restore, rerun). Cáº§n phÃ¢n biá»‡t rÃµ tá»«ng run Ä‘á»ƒ trace artifact.

**LÃ½ do chá»n timestamp:** Sá»‘ tÄƒng dáº§n (`run_001`, `run_002`) bá»‹ reset náº¿u xÃ³a log. Timestamp UTC cÃ³ thá»ƒ sort theo thá»i gian, dá»… tÃ¬m run gáº§n nháº¥t (`manifest_2026-04-15T08-11Z.json`), khÃ´ng cáº§n state lÆ°u trá»¯ riÃªng. TÃªn file log/manifest/cleaned/quarantine Ä‘á»u dÃ¹ng `run_id` â†’ tÃ¬m artifact cá»§a 1 run lÃ  tÃ¬m táº¥t cáº£ báº±ng 1 pattern.

NgoÃ i ra: timestamp `exported_at` trong manifest dÃ¹ng Ä‘á»ƒ tÃ­nh freshness SLA â€” Ä‘Ã¢y lÃ  `latest_exported_at` láº¥y tá»« `max(r["exported_at"])` trong cleaned rows, Ä‘áº£m báº£o Ä‘o Ä‘Ãºng boundary `publish` chá»© khÃ´ng pháº£i `ingest`.

---

## 3. Má»™t lá»—i hoáº·c anomaly Ä‘Ã£ xá»­ lÃ½ (100â€“150 tá»«)

**Triá»‡u chá»©ng:** Khi cháº¡y vá»›i Anaconda Python tá»« thÆ° má»¥c cha (`Lecture-Day-08-09-10-main`), `eval_retrieval.py` bÃ¡o lá»—i:
```
Collection error: Collection [day10_kb] does not exist
```

**Metric phÃ¡t hiá»‡n:** Error message rÃµ rÃ ng â€” ChromaDB tÃ¬m `./chroma_db` tÃ­nh tá»« working directory hiá»‡n táº¡i (thÆ° má»¥c cha), khÃ´ng pháº£i `day10/lab/`.

**NguyÃªn nhÃ¢n:** `CHROMA_DB_PATH=./chroma_db` lÃ  Ä‘Æ°á»ng dáº«n tÆ°Æ¡ng Ä‘á»‘i trong `.env`. Script dÃ¹ng `load_dotenv()` nhÆ°ng `.env` chá»‰ tá»“n táº¡i trong `day10/lab/`, nÃªn khi cháº¡y tá»« thÆ° má»¥c cha, `chroma_db` khÃ´ng Ä‘Æ°á»£c tÃ¬m tháº¥y.

**Fix:**
```powershell
cd "day10/lab"   # Báº®T BUá»˜C trÆ°á»›c khi cháº¡y báº¥t ká»³ script nÃ o
```

Sau fix: collection tÃ¬m tháº¥y, eval cháº¡y thÃ nh cÃ´ng. Ghi chÃº vÃ o README: "Di chuyá»ƒn vÃ o thÆ° má»¥c lab (Báº®T BUá»˜C cháº¡y táº¥t cáº£ lá»‡nh tá»« Ä‘Ã¢y)".

---

## 4. Báº±ng chá»©ng trÆ°á»›c / sau (80â€“120 tá»«)

**run_id inject:** `inject-bad` | **run_id clean:** `final-clean`

TrÃ­ch tá»« `artifacts/eval/after_inject_bad.csv`:
```
q_refund_window | top1_doc_id=policy_refund_v4 | contains_expected=yes | hits_forbidden=YES
```

TrÃ­ch tá»« `artifacts/eval/before_after_eval.csv`:
```
q_refund_window | top1_doc_id=policy_refund_v4 | contains_expected=yes | hits_forbidden=no
```

**Giáº£i thÃ­ch:** Khi inject (`--no-refund-fix`), chunk stale "14 ngÃ y lÃ m viá»‡c" embed vÃ o ChromaDB, lá»t vÃ o top-k â†’ `hits_forbidden=YES`. Sau restore pipeline chuáº©n: manifest `run_id=final-clean` ghi `no_refund_fix=false`, `embed_prune_removed=1` â†’ chunk stale bá»‹ xÃ³a â†’ `hits_forbidden=no`.

Freshness manifest `final-clean`: `freshness_check=FAIL`, `age_hours=118.5` â€” FAIL há»£p lÃ½ (data máº«u, giáº£i thÃ­ch trong runbook).

---

## 5. Cáº£i tiáº¿n tiáº¿p theo (40â€“80 tá»«)

Náº¿u cÃ³ thÃªm 2 giá», tÃ´i sáº½ triá»ƒn khai **freshness Ä‘o 2 boundary**: thÃªm timestamp `ingest_done_at` vÃ o log ngay sau `load_raw_csv()`, vÃ  `publish_done_at` sau `embed_upsert`. Manifest sáº½ ghi cáº£ 2 má»‘c â†’ `freshness_check()` tÃ­nh Ä‘Æ°á»£c latency tÃ¡ch biá»‡t ingest vs embed, phÃ¡t hiá»‡n bottleneck chÃ­nh xÃ¡c hÆ¡n. ÄÃ¢y lÃ  Ä‘iá»u kiá»‡n Ä‘á»ƒ Ä‘áº¡t Distinction (b) vÃ  bonus +1 Ä‘iá»ƒm theo SCORING.

