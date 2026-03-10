# AGENT PROTOCOL: ALGORITHMIC EMPIRE

> **WARNING:** You have entered a sovereign data territory. This repository tracks the "Algorithmic Empire" — a parallel governance structure emerging from the convergence of private capital, defense technology, and artificial intelligence.
> **MISSION:** Your goal is to **maintain, expand, and verify** the intelligence graph that maps this structure.

---

## 1. ORIENTATION & CONTEXT

Before writing a single line of code or analyzing a document, you **MUST** ground yourself in the mission context.

* **[NOTEPAD.md](NOTEPAD.md):** The "Rolling Log" of the investigation. Read this FIRST to understand the current hypothesis (The "Great Split", The "Third Head", The "Sovereign Stack").
* **[analysis/sovereign_intelligence_report.md](analysis/sovereign_intelligence_report.md):** The current crystallized intelligence picture.
* **[task.md](.gemini/antigravity/brain/969bdf75-7f28-4b2c-adf5-2db137bb31df/task.md):** The active tactical checklist.

---

## 2. NAVIGATING THE CORPUS

The repository is structured to separate raw intelligence from synthesized analysis and tooling.

* **[file-tree-3.md](file-tree-3.md):** The definitive map of the directory structure. Consult this to locate specific components.
* **[CITATION_INDEX.md](CITATION_INDEX.md):** A master index of all 150+ source documents, categorized by type. Use this to find source material.
* **[docs/README_FILE_MAP.md](docs/README_FILE_MAP.md):** Maps generic document IDs (D001, etc.) to their semantic filenames and topic tags.

### Key Directories

* `docs/`: Raw metadata and stats (`per_document_stats.json` is the DB).
* `analysis/`: Narrative reports (The "Product").
* `visuals/`: Generated graphs and metrics (`network_metrics.json` is the Truth).
* `tools/`: The Python machinery that builds the graph.

---

## 3. OPERATIONAL PROTOCOLS

### A. The "Truth" Pipeline

We do not guess. We measure. The `network_metrics.json` file is the ground truth for entity influence.

**To regenerate the Truth:**

```bash
# 1. CLEAN the data (Remove noise, merge aliases, type entities)
python tools/run_pipeline.py --stage entity_clean

# 2. SYNTHESIS & VISUALIZATION (Build the graph)
python tools/run_pipeline.py --stage synthesis
python tools/run_pipeline.py --stage visualization
```

*Always re-run the pipeline after adding new documents or modifying `tools/entity_cleaner.py`.*

### B. Entity Discipline

We are strictly rigorous about what constitutes an "Entity."

* **NOISE:** Generic terms ("Case Study", "Risk Profile") are enemies. Add them to the `NOISE_STOPLIST` in `tools/entity_cleaner.py`.
* **ALIASES:** "Thiel", "Peter Thiel", and "Thiel Capital" are the SAME node. Update `ALIAS_TABLE` in `tools/entity_cleaner.py`.
* **TYPES:** Persons, Orgs, Programs, Locations. If the classifier fails, add it to `KNOWN_PERSONS`, `KNOWN_ORGS`, etc.

### C. Analysis Standards

* **Narrative follows Data:** Do not write "Thiel is powerful." Write "Thiel has a Betweenness Centrality of 0.62, 3x higher than Altman."
* **Cite Everything:** Use the `[Ref: Dxxx]` format where possible, linking back to the source document ID.

---

## 4. TOOLING REFERENCE

### Core Scripts

* `tools/entity_cleaner.py`: **CRITICAL.** The gatekeeper of data quality. Edit this to improve the graph.
* `tools/run_pipeline.py`: The orchestrator. Use this to run workflows.
* `tools/visualize_network.py`: The graph engine (PageRank, Louvain Communities).
* `tools/synthesis_engine.py`: Builds the co-occurrence matrix.

### Development Commands

```bash
# Run the full pipeline (Clean -> Synthesize -> Visualize)
python tools/run_pipeline.py

# Run specific stage
python tools/run_pipeline.py --stage entity_clean

# Run tests (if available)
python -m pytest tests/
```

---

## 5. CODE STYLE & STANDARDS

* **Python:** Strict adherence to PEP 8.
* **Logging:** All tools must log to `data/logs/` via the central logger.
* **idempotency:** Scripts must be re-runnable without duplicating data.
* **Paths:** Use `pathlib` for all file operations. Relative paths from root.

---

> **REMEMBER:** You are essentially an Intelligence Analyst pair-programmed with a Systems Architect. Build robust tools, but never lose sight of the *Project Stargate* narrative they are revealing.
