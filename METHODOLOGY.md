# Methodology

> How data flows from raw intelligence corpus to analytical products.

---

## 1. Data Chain of Custody

```
RAW CORPUS (70+ .md files)
    │
    ▼
PHASE 1: Inventory & Labeling ──────► docs/README_FILE_MAP.md
    │                                  (label, path, filename, topic tags)
    ▼
PHASE 2: Per-Document Metrics ──────► docs/per_document_stats.json
    │                                  (page count, citation count, major entities)
    ▼
PHASE 3: Entity Cleaning ──────────► docs/per_document_stats_clean.json
    │                                  (noise removed, aliases merged, types assigned)
    │                                  tools/entity_cleaner.py controls quality
    ▼
PHASE 4: Synthesis Matrix ─────────► docs/synthesis_matrix.json
    │                                  (entity co-occurrence across documents)
    │                                  tools/synthesis_engine.py
    ▼
PHASE 5: Network Computation ──────► visuals/network_metrics.json
    │                                  (PageRank, betweenness centrality, Louvain communities)
    │                                  tools/visualize_network.py
    ▼
PHASE 6: Edge Weight Formalization ► docs/actor_system_adjacency_matrix.md
    │                                  (typed relationships, composite edge weights)
    ▼
PHASE 7: Intelligence Products ────► analysis/sovereign_intelligence_report.md
                                       analysis/evidence_matrix.md
                                       analysis/timeline_the_great_split.md
                                       (strategic assessments grounded in computed metrics)
```

---

## 2. Phase Details

### Phase 1: Inventory & Labeling

**Script:** Manual + `tools/sovereign_citation_indexer.py`
**Input:** All text-like files in the corpus (.md, .pdf, .html, .txt)
**Output:** `docs/README_FILE_MAP.md`

Each document receives:
- **Label:** A unique identifier derived from primary topic tag (T## = Thiel network, S## = Surveillance, U## = Military AI, etc.)
- **Original Path:** Where the document was sourced from
- **Suggested Folder:** Proposed organizational category (02_ACTORS, 03_INFRA, 04_STACK, 05_NETWORK, 06_OPEN_QUESTIONS)
- **Topic Tags:** One or more from: `THIEL_NETWORK`, `EPSTEIN_NETWORK`, `BARAK_ISRAEL`, `YARVIN_IDEOLOGY`, `CORPORATE_HANDOFFS`, `MILITARY_AI_US`, `MILITARY_AI_CHINA`, `AI_GOVERNANCE`, `SURVEILLANCE`, `FINANCIAL_INFRASTRUCTURE`, `OTHER`

### Phase 2: Per-Document Metrics

**Script:** `tools/run_pipeline.py` (initial processing)
**Input:** Raw corpus files
**Output:** `docs/per_document_stats.json`, `docs/per_document_stats_thorough.json`

For each document:
- **Page Count:** For PDFs, via pdfinfo. For text, 500 words per page heuristic.
- **Citation Count:** First searches for a "References" section, then falls back to heuristic patterns (bracketed numerals, author-year).
- **Major Names:** Repeated sequences of 2-4 capitalized words extracted as candidate entities.

### Phase 3: Entity Cleaning

**Script:** `tools/entity_cleaner.py`
**Input:** `docs/per_document_stats.json`
**Output:** `docs/per_document_stats_clean.json`, `docs/cleaning_report.json`

Three quality gates:
1. **NOISE_STOPLIST:** Removes generic terms that pollute the graph ("Case Study", "Risk Profile", "Executive Summary", etc.)
2. **ALIAS_TABLE:** Merges variant names to canonical forms ("Thiel" + "Peter Thiel" + "Thiel Capital" → "Peter Thiel")
3. **KNOWN_PERSONS / KNOWN_ORGS:** Explicit entity type assignment where automated classification fails

### Phase 4: Synthesis Matrix

**Script:** `tools/synthesis_engine.py`
**Input:** Cleaned per-document stats
**Output:** `docs/synthesis_matrix.json`

Builds a document × entity co-occurrence matrix:
- For each entity pair (A, B), counts the number of documents where both appear
- Stores as `{"entity_a": "...", "entity_b": "...", "shared_documents": N}`
- This matrix is the input for all graph computations

### Phase 5: Network Computation

**Script:** `tools/visualize_network.py`
**Input:** `docs/synthesis_matrix.json`
**Output:** `visuals/network_metrics.json`, `visuals/sovereign_network.*`

Algorithms applied:
- **PageRank:** Identifies the most structurally important entities in the network
- **Betweenness Centrality:** Identifies bridge entities that connect disparate clusters
- **Louvain Community Detection:** Identifies natural groupings/clusters of entities
- **Degree Distribution:** Measures connectivity of each node

Output formats: Interactive HTML (2D/3D), GEXF (Gephi), JSON, Mermaid, PNG export

### Phase 6: Actor-System Adjacency Matrix

**Document:** `docs/actor_system_adjacency_matrix.md`
**Input:** Synthesis matrix + manual analyst synthesis
**Output:** Formal typed edge weights

Relationship Type Taxonomy:
| Code | Type | Base Weight |
|------|------|-------------|
| OWN | Ownership / Founder | 1.00 |
| INV | Investor | 0.80 |
| CON | Contract Authority | 0.90 |
| PER | Personnel Placement | 0.75 |
| GOV | Governance / Policy | 0.85 |
| PAR | Partnership / Alliance | 0.70 |
| DEP | Dependency | 0.65 |

**Composite Edge Weight (CEW) Formula:**
$$CEW = \frac{\sum_{i}(BaseWeight_i \times EvidenceMultiplier_i)}{N_{max}}$$

Where $EvidenceMultiplier$ derives from the Authentication Confidence Score (NOTEPAD.md §7.0).

### Phase 7: Intelligence Products

**Input:** All preceding phases
**Output:** `analysis/*.md`

Products follow the principle: **Narrative follows data.**
- Claims cite specific metrics (e.g., "Betweenness Centrality of 0.62")
- Document references use `[Ref: Dxxx]` format linking to APPENDIX labels
- Confidence levels track to the Authentication Confidence Scoring scale

---

## 3. Authentication Confidence Scoring

All systems inventoried in the 7-layer operational stack (NOTEPAD.md §7) use this scale:

| Score | Meaning |
|-------|---------|
| 1.00 | Confirmed via declassified primary documents, official government releases, or irrefutable forensic evidence |
| 0.95–0.99 | Multi-source triangulation (leaked primary + independent journalism + official indirect acknowledgment) |
| 0.90–0.94 | Official corporate publications, government procurement records, or Congressional testimony |
| 0.80–0.89 | Credible multi-source reporting with partial official corroboration |
| < 0.80 | Contextual inference, structural analysis, or single-source reporting |

---

## 4. Regeneration

All computational artifacts can be regenerated from the raw corpus:

```bash
# Full pipeline
python tools/run_pipeline.py

# Individual stages
python tools/run_pipeline.py --stage entity_clean
python tools/run_pipeline.py --stage synthesis
python tools/run_pipeline.py --stage visualization

# Rebuild citation index
python tools/sovereign_citation_indexer.py

# Rebuild APPENDIX.md
python tools/appendix_regenerator.py
```

---

## 5. Known Limitations

1. **Citation Heuristics:** Citation counts for .md and .txt files use pattern matching and may over- or under-estimate actual citation counts.
2. **Entity Extraction:** Major names are extracted via capitalization heuristics, not NER models. Some entities may be missed or mis-typed.
3. **Topic Tagging:** Based on keyword matching against filenames and extracted entities. Documents tagged `OTHER` require manual review.
4. **Co-occurrence ≠ Causation:** Entity co-occurrence in documents indicates contextual association, not necessarily direct relationship.
5. **Temporal Gaps:** The corpus covers 1991–2026 unevenly. Dense coverage for 2017–2026, sparse for 1991–2010.
