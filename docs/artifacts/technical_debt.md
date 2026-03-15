# TECHNICAL DEBT LOG: BUNUELOS_TUREDONDITO

**Status:** ACTIVE  
**Last Updated:** 2026-03-14  
**Project Phase:** Phase 2 (MVP) - Stage 2.1 (Validation)

---

## 🏗️ Architectural Debt

### [TD-001] Monolithic Orchestrator (`main.py`)
*   **Description:** The `main.py` script currently handles data fetching, validation orchestration, cloud certification, and multi-table audit logging.
*   **Impact:** As the project scales to `train` and `forecast` commands, the file may become a "God Object," making unit testing and maintenance significantly harder.
*   **Strategy:** Refactor into specialized service classes (e.g., `IngestionService`, `AuditService`, `CloudStorageAdapter`).
*   **Priority:** MEDIUM

### [TD-002] Lack of Resilience (Retry Logic)
*   **Description:** External integrations (Supabase DB, Supabase Storage/S3) lack automated retry mechanisms for transient network failures.
*   **Impact:** Occasional micro-outages will cause the entire pipeline to fail, requiring manual intervention.
*   **Strategy:** Implement decorators or libraries (like `tenacity`) for exponential backoff retries on IO operations.
*   **Priority:** LOW

---

## 📊 Data & Performance Debt

### [TD-003] Inefficient Delta Detection (Full Download for Hash)
*   **Description:** The system downloads 100% of the source table to calculate the `Semantic Fingerprint` before deciding if it should process it.
*   **Impact:** High network costs and latency as data volume grows to millions of rows.
*   **Strategy:** Implement a "Pre-flight Check" that queries only metadata (row counts, max timestamps, or server-side hashes) before full data transfer.
*   **Priority:** HIGH (Scalability critical)

### [TD-004] Probabilistic Semantic Fingerprint (Sample-Based)
*   **Description:** To maintain high performance, the `semantic_hash` currently includes only a sample of the first 5 rows of the dataset.
*   **Impact:** There is a non-zero probability that data changes in the middle of a large table might not be detected if the row count and schema remain identical.
*   **Strategy:** Implement a more robust (but efficient) hashing mechanism, such as hashing a randomized sample or specific "anchor" columns.
*   **Priority:** MEDIUM

---

## ⚙️ Configuration & Operational Debt

### [TD-005] Hardcoded Profiling Thresholds
*   **Description:** Limits such as the categorical "top 20" categories and the "5-row sample" are hardcoded in `src/validator.py`.
*   **Impact:** Changes to these business requirements require code modifications rather than simple configuration updates.
*   **Strategy:** Move all profiling and validation thresholds to `config.yaml` under the `validation` section.
*   **Priority:** LOW

### [TD-006] Synchronous Execution
*   **Description:** Parallel table validation is not implemented; tables are processed sequentially.
*   **Impact:** Longer execution times for the `load` command as the number of tables in the contract increases.
*   **Strategy:** Utilize `asyncio` or `concurrent.futures` to validate multiple tables in parallel.
*   **Priority:** LOW

---

## 📈 Summary of Debt Exposure

| Category | High Priority | Medium Priority | Low Priority |
| :--- | :---: | :---: | :---: |
| Architecture | 0 | 1 | 1 |
| Data/Perf | 1 | 1 | 0 |
| Operations | 0 | 0 | 2 |

> [!TIP]
> **Recommendation:** Address **[TD-003]** (Inefficient Delta Detection) before moving from MVP to Full Scale production, as this will have the highest impact on infrastructure costs.
