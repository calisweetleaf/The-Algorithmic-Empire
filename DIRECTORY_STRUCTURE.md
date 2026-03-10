# Directory Structure

> Annotated map of the repository. Updated: 2026-03-09.

```
algorithmic_empire/
│
├── .gitignore                         # Git ignore rules
├── README.md                          # Project overview, provenance, and structure
├── PROVENANCE.md                      # Full AI toolchain disclosure and chain of custody
├── METHODOLOGY.md                     # Analytical pipeline and data processing methodology
├── DIRECTORY_STRUCTURE.md             # This file
├── AGENTS.md                          # Agent protocol instructions for AI contributors
├── NOTEPAD.md                         # AI-generated investigation reasoning log (UNTOUCHED)
├── MEMORY.md                          # Project state memory for session continuity
├── CONTEXT.md                         # Session context for agent handoffs
├── CITATION_INDEX.md                  # Auto-generated citation index (105 files)
├── citation_config.yaml               # Citation indexer configuration
├── rules_of_engagement.md             # Somnus Sovereign Defense ROE framework
├── requirements.txt                   # Raw Python dependency list
├── requirements.install.txt           # Sanitized install manifest (use this)
│
├── *.md (70+ files)                   # RAW INTELLIGENCE CORPUS
│   │                                  # Each file is a self-contained OSINT report
│   │                                  # covering: defense AI, surveillance, entity
│   │                                  # networks, military systems, corporate handoffs
│   │                                  # Topics tagged in docs/README_FILE_MAP.md
│   ├── Thiel-related (15+ files)      # Peter Thiel network analysis
│   ├── Altman-related (10+ files)     # Sam Altman / OpenAI analysis
│   ├── Anthropic-related (5 files)    # Anthropic governance and hidden models
│   ├── Military AI (10+ files)        # Defense AI systems and leaks
│   ├── Israel/Iran (3 files)          # Geopolitical conflict intelligence
│   └── Anomalous tech (5+ files)      # Aerospace, propulsion, anomalies
│
├── analysis/                          # SYNTHESIZED INTELLIGENCE PRODUCTS
│   ├── sovereign_intelligence_report.md   # PRIMARY: Strategic assessment
│   ├── evidence_matrix.md                 # Cross-referenced evidence grid
│   ├── timeline_the_great_split.md        # 1991-2017 lineage reconstruction
│   ├── military_industrial_complex_deep_dive.md
│   ├── stargate_anomaly_dossier.md        # Stargate initiative analysis
│   ├── network_topology_report.md         # Network structure analysis
│   ├── collection_requirements.md         # Outstanding collection gaps
│   ├── synthesis_report.md                # Synthesis methodology report
│   ├── actor_system_adjacency_matrix.md   # Updated actor-system edges (2026-02-18)
│   ├── arcs_synthesis_*.md                # ARCS auto-generated synthesis runs
│   └── automated_synthesis_matrix.json    # Machine-generated synthesis data
│
├── docs/                              # METADATA, INDEXES, PROCESS RECORDS
│   ├── README_FILE_MAP.md                 # *** BASELINE: label → path → tag mapping ***
│   ├── APPENDIX.md                        # *** Full SIGINT appendix (150 docs) ***
│   ├── actor_system_adjacency_matrix.md   # *** Formal edge weights + formulas ***
│   ├── entity_network.md                  # Top entity co-occurrence pairs
│   ├── synthesis_matrix.json              # Raw entity co-occurrence matrix
│   ├── per_document_stats.json            # Original per-doc metrics
│   ├── per_document_stats_clean.json      # Cleaned entity statistics
│   ├── per_document_stats_thorough.json   # Thorough re-extraction pass
│   ├── citation_recount_log.json          # Citation verification log
│   ├── cleaning_report.json               # Entity cleaning report
│   ├── PROCESS_LOG.md                     # Pipeline execution audit trail
│   ├── HANDOFF_SCHEMA.json                # Multi-agent handoff contract schema
│   ├── ROLE_EXECUTION_MATRIX.md           # Agent role specializations
│   ├── STATE_SNAPSHOT_2026-02-17.md       # Verified runtime state snapshot
│   ├── MOBILE_RESEARCH_GUIDE_2026-02-18.md
│   ├── file-tree.md                       # Historical file tree (2026-02-08)
│   └── FILETREE2.MD                       # Historical file tree (alt)
│
├── tools/                             # PYTHON ANALYSIS PIPELINE
│   ├── run_pipeline.py                    # Orchestrator: clean → synthesize → visualize
│   ├── entity_cleaner.py                  # *** CRITICAL: noise/alias/type gatekeeper ***
│   ├── synthesis_engine.py                # Co-occurrence matrix builder
│   ├── visualize_network.py               # PageRank, Louvain, graph rendering
│   ├── sovereign_citation_indexer.py      # Corpus citation index generator
│   ├── sovereign_analysis_tool.py         # Analytical query interface
│   ├── citation_recount.py                # Citation re-verification utility
│   ├── appendix_regenerator.py            # APPENDIX.md rebuilder
│   ├── python_production_doctor.py        # ARCS code health analyzer
│   ├── run_tonight_plan.py                # Execution plan runner
│   └── tmp_trim_prod_doctor.py            # Temporary utility
│
├── visuals/                           # NETWORK GRAPHS & VISUALIZATIONS
│   ├── network_metrics.json               # *** GROUND TRUTH: PageRank, centrality ***
│   ├── sovereign_network.html             # Interactive 2D network visualization
│   ├── sovereign_network_3d.html          # Interactive 3D network visualization
│   ├── sovereign_network.gexf             # Gephi export
│   ├── sovereign_network_advanced.gexf    # Advanced Gephi export
│   ├── sovereign_network.json             # JSON graph data
│   ├── sovereign_network.mmd              # Mermaid diagram source
│   ├── intelligence_report.md             # Visual intelligence report
│   └── exports/                           # Rendered image exports
│       └── sovereign_network_8k_*.png     # High-res network render
│
├── reports/                           # MULTI-STAGE PIPELINE OUTPUTS
│   ├── stage1_evidence_curator.md         # Stage 1: Evidence curation
│   ├── stage1_evidence_curator_manifest.json
│   ├── stage2_edge_encoding.md            # Stage 2: Relationship encoding
│   ├── stage2_edge_encoding_manifest.json
│   ├── stage3_matrix_compute.md           # Stage 3: Matrix computation
│   ├── stage3_matrix_compute_manifest.json
│   ├── stage4_finisher.md                 # Stage 4: Final synthesis
│   ├── stage4_finisher_manifest.json
│   └── python_production_doctor/          # ARCS code health reports
│       ├── arcs_aggregate_report.md
│       ├── arcs_run_manifest.json
│       └── arcs_per_file/                 # Per-file health reports
│
├── ARCS/                              # AUTONOMOUS RECON & CORRELATION SYSTEM
│   ├── data_fusion.py                     # Intelligence synthesis engine
│   ├── attribution_engine.py              # Entity attribution analysis
│   ├── threat_aggregation.py              # Threat correlation engine
│   ├── network_telemetry.py               # Network analysis telemetry
│   ├── osint_orchestrator.py              # OSINT workflow orchestration
│   ├── corpus_ingestion_pipeline.py       # Document ingestion pipeline
│   ├── intelligence_database.py           # Intelligence storage layer
│   ├── browser_intelligence.py            # Web intelligence collection
│   ├── system_behavior.py                 # System behavioral analysis
│   ├── attribution-engine.md              # Attribution engine documentation
│   ├── PROJECT_DATABASE_DOCUMENTATION.md  # Database schema documentation
│   └── tests/                             # ARCS test suite
│       ├── conftest.py
│       ├── test_data_fusion.py
│       ├── test_network_telemetry.py
│       └── test_threat_aggregation.py
│
├── file-proccessor/                   # ENTERPRISE FILE PROCESSING SYSTEM
│   ├── universal_file_processors.py       # Multi-format file handling
│   ├── semantic_chunking.py               # Semantic text chunking
│   ├── semantic_chunking_rewrite.py       # Chunking rewrite
│   ├── sovereignty.py                     # Sovereign data processing
│   ├── persistent_processing_queue.py     # Queue management
│   ├── accelerated_file_processing.py     # Accelerated processing
│   ├── enhanced_file_manager.py           # Enhanced file management
│   ├── file_upload_system.py              # Upload system
│   ├── moonshine_output.py                # Moonshine integration
│   ├── test_processors.py                 # Processor tests
│   ├── pyproject.toml                     # Package config
│   ├── requirements.txt                   # Package dependencies
│   ├── setup_venv.ps1                     # Venv setup script
│   ├── PROCESSOR_COVERAGE.md              # Coverage documentation
│   └── *.md                               # Dev guides
│
├── config/                            # YAML CONFIGURATION FILES
│   ├── attribution.yaml                   # Attribution engine config
│   ├── behavioral.yaml                    # Behavioral analysis config
│   ├── data_fusion.yaml                   # Data fusion config
│   ├── roe_threat_mapping.yaml            # ROE threat mapping config
│   └── python_production_doctor.arcs.yaml # Production doctor config
│
├── data/                              # RUNTIME DATA STORES
│   ├── derived/                           # Computed edge/adjacency data (JSON)
│   ├── intelligence/                      # Intelligence databases
│   │   ├── arcs_intelligence.db           # ARCS intelligence database
│   │   ├── correlations.db                # Correlation database
│   │   ├── models/                        # Model storage
│   │   ├── storage/                       # Tiered storage (hot/warm/cold/frozen)
│   │   └── vectors/                       # Vector embeddings (empty)
│   └── logs/                              # Pipeline execution logs
│
├── models/                            # ML MODEL DIRECTORIES (empty placeholders)
│   ├── attribution/
│   ├── behavioral/
│   ├── data_fusion/
│   └── threat_classification/
│
├── templates/                         # OSINT PROFILE TEMPLATES
│   └── osint_profile_templates.md
│
├── maybe/                             # REM-CORE EXPERIMENTAL MODULES
│   ├── narrative_generator.py             # Narrative generation
│   ├── predictive_analyzer.py             # Predictive analysis
│   ├── threat_assessment.py               # Threat assessment
│   └── narrative-gen-test                 # Test file
│
├── pdf/                               # SOURCE PDFs
│   └── Anthropic Response to OSTP RFI (March 2025).pdf
│
└── personal-research/                 # PRIVATE (gitignored)
    └── [plasma/propulsion research]
```

## Key Files by Importance

| Priority | File | Role |
|----------|------|------|
| 1 | `docs/README_FILE_MAP.md` | Baseline taxonomy: every document labeled, pathed, tagged |
| 2 | `docs/APPENDIX.md` | Full corpus index expanded from the baseline |
| 3 | `docs/actor_system_adjacency_matrix.md` | Formal actor-system edge weights with CEW formula |
| 4 | `visuals/network_metrics.json` | Ground truth: computed PageRank, centrality, community |
| 5 | `analysis/sovereign_intelligence_report.md` | Primary strategic intelligence product |
| 6 | `docs/entity_network.md` | Entity co-occurrence strength rankings |
| 7 | `docs/synthesis_matrix.json` | Raw co-occurrence data (machine-readable) |
| 8 | `NOTEPAD.md` | AI reasoning log (GPT-5.3/Opus 4.6 raw output) |
| 9 | `tools/entity_cleaner.py` | Data quality gatekeeper (aliases, noise, types) |
| 10 | `CITATION_INDEX.md` | Auto-generated citation index across corpus |
