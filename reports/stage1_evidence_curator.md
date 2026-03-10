# STAGE 1 — EVIDENCE CURATOR REPORT
**Run Date:** 2026-02-18 02:21  
**Stage:** 1 of 4  
**Data:** `visuals/network_metrics.json` (live) + `docs/synthesis_matrix.json` (live)  

---

## 1. GATE STATUS

| Criterion | Status |
|---|---|
| All edges have ≥1 file anchor | ✅ PASS |
| All edges have ≥1 confidence note | ✅ PASS |
| Duplicate citation variants resolved | ✅ PASS |
| Canonical source IDs from README_FILE_MAP.md | ✅ PASS |
| All metrics from live pipeline run | ✅ PASS |

---

## 2. LIVE GRAPH STATS

| Metric | Value |
|---|---|
| Nodes | 271 |
| Edges | 2076 |
| Density | 0.056745 |
| Avg Clustering | 0.886043 |
| Communities | 18 |

---

## 3. TOP 20 PAGERANK (live)

| Rank | Entity | PageRank | Betweenness | Degree | Community |
|---|---|---|---|---|---|
| 1 | **Peter Thiel** | 0.02773 | 0.48430 | 135 | 8 |
| 2 | **Anduril Industries** | 0.01824 | 0.27093 | 90 | 8 |
| 3 | **Sam Altman** | 0.01742 | 0.26345 | 88 | 8 |
| 4 | **Palantir Technologies** | 0.01635 | 0.17684 | 83 | 8 |
| 5 | **Founders Fund** | 0.01567 | 0.09039 | 80 | 8 |
| 6 | **Elon Musk** | 0.01356 | 0.10486 | 71 | 8 |
| 7 | **Lockheed Martin** | 0.01264 | 0.32913 | 55 | 8 |
| 8 | **Project Maven** | 0.01106 | 0.13050 | 55 | 8 |
| 9 | **Silicon Valley** | 0.01085 | 0.05816 | 55 | 8 |
| 10 | **United States** | 0.01052 | 0.19650 | 45 | 8 |
| 11 | **Hydrazine Capital** | 0.01001 | 0.09104 | 51 | 239 |
| 12 | **Valar Ventures** | 0.00894 | 0.01990 | 45 | 8 |
| 13 | **Air Force** | 0.00815 | 0.04363 | 37 | 8 |
| 14 | **Mithril Capital** | 0.00774 | 0.00932 | 41 | 8 |
| 15 | **Claude Gov** | 0.00774 | 0.04787 | 32 | 8 |
| 16 | **Five Eyes** | 0.00706 | 0.02707 | 35 | 8 |
| 17 | **Artificial Intelligence** | 0.00665 | 0.02843 | 31 | 8 |
| 18 | **Lattice OS** | 0.00648 | 0.01434 | 33 | 8 |
| 19 | **Skinwalker Ranch** | 0.00619 | 0.02652 | 25 | 8 |
| 20 | **OpenAI Startup Fund** | 0.00598 | 0.01943 | 29 | 239 |

---

## 4. TOP 20 BETWEENNESS (live)

| Rank | Entity | Betweenness | PageRank | Degree |
|---|---|---|---|---|
| 1 | **Peter Thiel** | 0.48430 | 0.02773 | 135 |
| 2 | **Lockheed Martin** | 0.32913 | 0.01264 | 55 |
| 3 | **Anduril Industries** | 0.27093 | 0.01824 | 90 |
| 4 | **Sam Altman** | 0.26345 | 0.01742 | 88 |
| 5 | **United States** | 0.19650 | 0.01052 | 45 |
| 6 | **Palantir Technologies** | 0.17684 | 0.01635 | 83 |
| 7 | **Project Maven** | 0.13050 | 0.01106 | 55 |
| 8 | **Elon Musk** | 0.10486 | 0.01356 | 71 |
| 9 | **Hydrazine Capital** | 0.09104 | 0.01001 | 51 |
| 10 | **Founders Fund** | 0.09039 | 0.01567 | 80 |
| 11 | **Silicon Valley** | 0.05816 | 0.01085 | 55 |
| 12 | **Claude Gov** | 0.04787 | 0.00774 | 32 |
| 13 | **Air Force** | 0.04363 | 0.00815 | 37 |
| 14 | **Khosla Ventures** | 0.03029 | 0.00474 | 23 |
| 15 | **Artificial Intelligence** | 0.02843 | 0.00666 | 31 |
| 16 | **Five Eyes** | 0.02707 | 0.00706 | 35 |
| 17 | **Skinwalker Ranch** | 0.02652 | 0.00619 | 25 |
| 18 | **Valar Ventures** | 0.01990 | 0.00894 | 45 |
| 19 | **OpenAI LP** | 0.01964 | 0.00479 | 24 |
| 20 | **OpenAI Startup Fund** | 0.01943 | 0.00598 | 29 |

---

## 5. PRIMARY ACTOR METRICS

| Actor | PageRank | Betweenness | Degree | Community | In Graph |
|---|---|---|---|---|---|
| Peter Thiel  | 0.02773  | 0.48430  | 135  | 8  | ✅ |
| Sam Altman   | 0.01742   | 0.26345   | 88   | 8   | ✅ |
| Larry Ellison| 0.00284 | 0.00141 | 9 | 171 | ✅ ⚠️ low-freq |
| Eric Schmidt | N/A | N/A | N/A | N/A | ❌ NOT IN GRAPH |
| Elon Musk    | 0.01356    | 0.10486    | 71    | 8    | ✅ |

> **Eric Schmidt gap confirmed:** zero hits as named entity in `per_document_stats_clean.json`.
> Influence encoded only under institutional nodes (NSCAI, Google DeepMind, Anthropic).
> **Larry Ellison gap confirmed:** degree=9, community=171 (Anthropic funding cluster).
> Enters graph via Anthropic investment — NOT via Oracle/JWCC/CIA chain.

---

## 6. KEY CO-OCCURRENCE ANCHORS (synthesis_matrix.json)

| Pair | Shared Docs |
|---|---|
| Founders Fund ↔ Peter Thiel | 33 |
| Anduril Industries ↔ Palantir Technologies | 29 |
| Palantir Technologies ↔ Peter Thiel | 27 |
| Peter Thiel ↔ Sam Altman | 23 |
| Anduril Industries ↔ Peter Thiel | 23 |
| Elon Musk ↔ Peter Thiel | 20 |
| Project Stargate ↔ Sam Altman | 9 |
| Anduril Industries ↔ Sam Altman | 9 |
| Scale AI ↔ Anduril Industries | 9 |
| Claude Gov ↔ Anduril Industries | 6 |
| Larry Ellison ↔ Peter Thiel | 3 |
| Larry Ellison ↔ Sam Altman | 2 |

---

## 7. CITATION DEDUPLICATION

Duplicate variants (corporate_reports copies of dispersion originals) suppressed.
Canonical IDs from `docs/README_FILE_MAP.md`.

| Canonical | Suppressed | Filename |
|---|---|---|
| T10 | T63 | Deep State AI Governance OSINT.md |
| T11 | T64 | algorithmic leviathan.md |
| T13 | T65 | Theil's Influence.md |
| T15 | T66 | thiel private sector state.md |
| T17 | T68 | Thiel Nexus.md |
| T20 | T71 | Altman's Covert Power Structure Analysis.md |
| T24 | T72 | Theils Covert Ops.md |
| T27 | T73 | Thiel_Altman_Synthetic_Empire.md |
| T28 | T74 | altmans_synthetic_empire.md |
| T30 | T75 | Altmans Hidden Latus.md |
| T35 | T76 | Thiel Network International Matrices.md |
| S05 | S09 | Altman Control.md |
| O04 | O14 | Opaque Empire of Sam Altman.md |
| O12 | O15 | Altman Nexus.md |

**Total suppressed:** 14  |  **Canonical retained:** 62+

---

## 8. COLLECTION GAPS CONFIRMED BY TOOL

1. **Eric Schmidt — NOT IN GRAPH.** Zero named-entity hits. Governance influence is real but
   the corpus indexes it under NSCAI/Google/Anthropic nodes only.
2. **Larry Ellison — SEVERELY UNDERREPRESENTED.** degree=9,
   PR=0.00284. Only U11 dedicated to Oracle/IC chain.
3. **Project Stargate isolated from Thiel core.** Community 239 (not 8).
   Peter Thiel ↔ Project Stargate: 6 docs.
4. **Scale AI subdued.** degree=27, PR=0.00548.
   Data-labeling backbone role underrepresented relative to structural importance.

---

**[END STAGE 1]** Gate: PASS → proceed to Stage 2