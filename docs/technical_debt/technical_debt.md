# TECHNICAL DEBT LOG: BUNUELOS_TUREDONDITO

**Status:** ACTIVE  
**Last Updated:** 2026-03-15  
**Project Phase:** Phase 2 (MVP) - Stage 2.2 (Ingestion)

---

## 🏗️ Architectural Debt

### [TD-001] Monolithic Orchestrator (`main.py`)
*   **Description:** The `main.py` script currently handles data fetching, validation orchestration, cloud certification, and multi-table audit logging.
*   **Impact:** As the project scales to `train` and `forecast` commands, the file may become a "God Object," making unit testing and maintenance significantly harder.
*   **Strategy:** Refactor into specialized service classes (e.g., `IngestionService`, `AuditService`, `CloudStorageAdapter`).
*   **Priority:** MEDIUM

### [TD-002] Lack of Resilience (Retry Logic) - PARTIALLY RESOLVED
*   **Description:** External integrations in `UnifiedIngestor` now use `@backoff_retry`, but `main.py` and some specific IO operations in `connector` still lack a standardized retry mechanism.
*   **Impact:** Handled in core ingestion, but orchestration might still fail on transient Supabase API errors.
*   **Strategy:** Standardize the use of the `@backoff_retry` decorator across all service layers.
*   **Priority:** LOW (Mitigated)

---

## 📊 Data & Performance Debt

### [TD-003] Inefficient Delta Detection - PARTIALLY RESOLVED
*   **Description:** The system now uses row-count pointers and audit states to determine `SKIP/FULL/INCREMENTAL`. However, it still lacks a server-side hash check for content-only changes (same row count, different content).
*   **Impact:** Low for historical tables, but could miss data corrections in the source.
*   **Strategy:** Implement a "Pre-flight Check" that uses database triggers or server-side functions (RPC) to get a content hash.
*   **Priority:** MEDIUM

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

### [TD-007] Fragile DVC Status Parsing
*   **Description:** `UnifiedIngestor` parses the string output of `dvc status` to verify synchronization.
*   **Impact:** High risk of failure if the DVC CLI changes its output format, language, or version.
*   **Strategy:** Use the DVC Python API (if available) or check for the existence of the `.dvc` file and its remote pointer directly via checksums.
*   **Priority:** MEDIUM

### [TD-008] Permissive Bootstrap Fallback
*   **Description:** The Gatekeeper automatically triggers `is_bootstrap = True` if the governance query fails, potentially masking connectivity issues.
*   **Impact:** Could allow invalid data into the pipeline during a temporary Supabase outage instead of failing safely.
*   **Strategy:** Implement a more robust "Health Check" dedicated to the governance connection before deciding to fallback to Bootstrap mode.
*   **Priority:** MEDIUM

### [TD-009] Partial Validation for NO_DATA
*   **Description:** `main.py` relaxes structural validation when a source is empty.
*   **Impact:** If a table is empty but its DDL has changed incompatibly, the error is only caught when data eventually arrives.
*   **Strategy:** Perform structural validation against the source DDL/Schema even if the result set is empty.
*   **Priority:** LOW

---

## 📈 Summary of Debt Exposure

| Category | High Priority | Medium Priority | Low Priority |
| :--- | :--- : | :--- : | :--- : |
| Architecture | 0 | 1 | 2 |
| Data/Perf | 0 | 3 | 0 |
| Operations | 0 | 2 | 1 |

> [!TIP]
> **Recommendation:** Address **[TD-003]** (Inefficient Delta Detection) before moving from MVP to Full Scale production, as this will have the highest impact on infrastructure costs.
