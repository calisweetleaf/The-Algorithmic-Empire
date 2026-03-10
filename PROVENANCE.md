# Provenance

> Full disclosure of the AI systems, tools, and human roles that produced this repository.

---

## Human Contributions

### Role: Researcher, Curator, Director

The single human researcher performed:

1. **Source Collection:** Gathered 150+ OSINT documents from public sources including government procurement records, patent databases, corporate filings, Congressional testimony, academic papers, flight tracking data, leaked technical documents (publicly surfaced), news reporting, and social media analysis.

2. **Investigation Direction:** Formulated the core hypotheses ("The Great Split," "The Three Heads," "Recursive Sovereignty"), defined the entity taxonomy, and directed the analytical focus.

3. **Labeling Taxonomy:** Designed the label system (T## for Thiel network, S## for surveillance, U## for military AI, etc.) and topic tag vocabulary (THIEL_NETWORK, EPSTEIN_NETWORK, MILITARY_AI_US, AI_GOVERNANCE, etc.).

4. **Tool Development:** Built or maintained the enterprise file processor (`file-proccessor/`), ARCS modules, and the MCP server infrastructure that AI agents utilized.

5. **Quality Control:** Reviewed, directed, and approved the outputs of AI agents at each stage of the pipeline.

### What the Human Did NOT Write

- `NOTEPAD.md` — This is the raw reasoning output of the AI models. The human did not edit or author it.
- `analysis/sovereign_intelligence_report.md` — AI-synthesized from the corpus.
- `docs/entity_network.md` — Computationally generated.
- `visuals/network_metrics.json` — Computationally generated.
- Most files in `reports/` — Multi-stage pipeline outputs from AI agents.

---

## AI Systems Used

### GPT-5.3-CODEX-XHIGH (OpenAI)

- **Access:** Via Codex CLI with full tool permissions
- **Capabilities Used:** File system read/write, shell execution, MCP tool calling, memory persistence, multi-step reasoning
- **Contributions:** Corpus ingestion, entity extraction, document statistics computation, synthesis matrix generation, NOTEPAD.md reasoning, intelligence report drafting

### Claude Opus 4.6 Thinking (Anthropic)

- **Access:** Via Claude Code with full tool permissions
- **Capabilities Used:** Extended thinking, file system access, terminal execution, MCP integration, memory persistence
- **Contributions:** Entity network analysis, adjacency matrix formulation, code development (ARCS modules, pipeline tools), intelligence report synthesis, code health analysis

### Shared Infrastructure

Both models operated through:

- **MCP Server:** Custom Model Context Protocol server with 55+ tools for memory, file operations, shell execution, visual automation, and code analysis
- **BB7 Exoskeleton:** Multi-model distributed cognition framework enabling role specialization (planner_reasoner, builder_executor, finisher_polisher) with handoff artifacts
- **ARCS Modules:** Autonomous Reconnaissance & Correlation System providing data fusion, attribution, threat aggregation, and corpus ingestion capabilities
- **Enterprise File Processor:** Multi-format document processing with semantic chunking
- **REM-core:** Experimental modules for narrative generation, predictive analysis, and threat assessment

---

## Artifact Provenance Map

| Artifact | Producer | Method |
|----------|----------|--------|
| Root `*.md` corpus (70+ files) | Human | Manual OSINT collection |
| `docs/README_FILE_MAP.md` | AI (Codex/Opus) | Automated labeling from file inventory |
| `docs/per_document_stats.json` | AI (Codex) | Python script extraction (pages, cites, entities) |
| `docs/per_document_stats_thorough.json` | AI (Codex) | Re-extraction with refined heuristics |
| `docs/per_document_stats_clean.json` | AI (Opus) | Entity cleaning pass |
| `docs/APPENDIX.md` | AI (Codex) | Generated from per_document_stats |
| `docs/synthesis_matrix.json` | AI (Codex/Opus) | `tools/synthesis_engine.py` execution |
| `docs/entity_network.md` | AI (Opus) | Co-occurrence computation |
| `docs/actor_system_adjacency_matrix.md` | AI (Opus) | Manual synthesis + formal edge weight formulas |
| `visuals/network_metrics.json` | AI (Codex/Opus) | `tools/visualize_network.py` (PageRank, Louvain) |
| `visuals/sovereign_network.*` | AI (Codex/Opus) | Graph rendering pipeline |
| `analysis/sovereign_intelligence_report.md` | AI (Codex/Opus) | Multi-pass synthesis from full corpus |
| `analysis/evidence_matrix.md` | AI (Opus) | Cross-reference analysis |
| `analysis/timeline_the_great_split.md` | AI (Opus) | Historical reconstruction |
| `NOTEPAD.md` | AI (Codex + Opus) | Raw reasoning log during investigation |
| `CITATION_INDEX.md` | AI (Codex) | `tools/sovereign_citation_indexer.py` |
| `reports/stage*` | AI (Opus) | Distributed cognition pipeline stages |
| `ARCS/*.py` | AI (Codex/Opus) + Human | Code modules (AI-developed under human direction) |
| `tools/*.py` | AI (Codex/Opus) + Human | Analysis pipeline (AI-developed under human direction) |
| `file-proccessor/*` | Human + AI | Enterprise processor (human-originated, AI-enhanced) |
| `config/*.yaml` | AI (Opus) | Generated from system requirements |
| `rules_of_engagement.md` | AI (Opus) | Framework document |

---

## Verification

To verify the computational artifacts are reproducible from the source corpus:

```bash
# Regenerate the entity network and metrics from scratch
python tools/run_pipeline.py --stage entity_clean
python tools/run_pipeline.py --stage synthesis
python tools/run_pipeline.py --stage visualization
```

The pipeline reads the root `*.md` corpus, applies `tools/entity_cleaner.py` rules, and regenerates:
- `docs/synthesis_matrix.json`
- `docs/entity_network.md`
- `visuals/network_metrics.json`
- `visuals/sovereign_network.*`

---

## Ethical Note

No AI system was used to fabricate evidence. The AI systems processed, analyzed, and synthesized existing publicly available documents. All analytical claims in the intelligence products are traceable to cited sources within the corpus. Confidence scores are assigned per the methodology documented in `NOTEPAD.md` Section 7.0.
