# MOBILE RESEARCH GUIDE
## Sovereign OSINT Deep-Search Operations | 2026-02-18

**Classification:** UNCLASSIFIED // FOUO EQUIVALENT — OPERATIONAL GUIDE  
**Date:** 2026-02-18  
**Analyst:** SOVEREIGN OSINT CELL  
**Mission:** Evidence-backed edge expansion for the adjacency matrix across three critical lanes  

---

## QUICK ORIENTATION

This guide is optimized for mobile deployment. All file paths are absolute from `C:\Users\treyr\Documents\algorithmic_empire`. Copy-paste ready prompts included. Reference the base workflow in `workflows.md` Section 5.2 for MCP tool operations.

**Current Ground Truth (from NOTEPAD.md):**
- Third Head confirmed: Eric Schmidt (Blue Team / Soft Power)
- Anthropic = dual-use regulatory capture vehicle (Claude Gov betweenness: 0.1090, rank #9)
- Scale AI = structurally invisible but DoD data labeling backbone
- Ellison underrepresentation confirmed - Oracle is Stargate compute substrate
- Sovereign Stack 7-layer model operational

---

## 1. PHONE PACK CHECKLIST

### 15 MUST BRING FILES (Core Corpus)

| # | File Path | Purpose | Priority |
|---|-----------|---------|----------|
| 1 | `NOTEPAD.md` | Rolling investigation log, current hypotheses | CRITICAL |
| 2 | `analysis/actor_system_adjacency_matrix.md` | Relationship taxonomy, CEW/ARS scoring grammar | CRITICAL |
| 3 | `analysis/collection_requirements.md` | Tier 1-4 collection targets and gaps | CRITICAL |
| 4 | `CITATION_INDEX.md` | Master source document registry (150+ sources) | CRITICAL |
| 5 | `docs/README_FILE_MAP.md` | Document ID mapping (D001, T01, etc.) | CRITICAL |
| 6 | `workflows.md` | MCP tool workflows, especially Section 5.2 | CRITICAL |
| 7 | `analysis/sovereign_intelligence_report.md` | Crystallized intelligence picture | HIGH |
| 8 | `analysis/evidence_matrix.md` | Evidence traceability clusters | HIGH |
| 9 | `analysis/network_topology_report.md` | Quantitative ground truth (PageRank, Betweenness) | HIGH |
| 10 | `docs/entity_network.md` | Major convergence corridors | HIGH |
| 11 | `docs/APPENDIX.md` | Topic bucket index | MEDIUM |
| 12 | `docs/TONIGHT_EXECUTION_PLAN_2026-02-18.md` | Active tactical checklist | MEDIUM |
| 13 | `visuals/network_metrics.json` | Ground truth for entity influence | MEDIUM |
| 14 | `AGENTS.md` | Agent protocol and operational standards | MEDIUM |
| 15 | `docs/STATE_SNAPSHOT_2026-02-17.md` | Baseline state reference | LOW |

### 5 REFERENCE ADD-ONS (Lane-Specific)

| # | File Path | Purpose | Lane |
|---|-----------|---------|------|
| R1 | `Anthropic AI_ Origins and Network.md` | Anthropic founding network, Schmidt investment | A |
| R2 | `Anthropic's Global AI Governance.md` | Anthropic governance architecture | A |
| R3 | `Stargate Program OSINT Deep Dive.md` | Stargate infrastructure, Ellison role | C |
| R4 | `Oracle Origins_ Intelligence, Databases, and Cold .md` | Oracle-CIA/NSA lineage | C |
| R5 | `Deep State AI Governance OSINT.md` | NSCAI, regulatory capture mechanisms | A/C |

---

## 2. MISSION PARAMETERS

### LANE A: ANTHROPIC (Dual-Use Regulatory Capture)

**Primary Targets:**
- Dario/Daniela Amodei (founders)
- Eric Schmidt (Series A investor)
- Google/Alphabet ($2B+ investment)
- AWS partnership ($4B)
- Claude Gov deployment

**Collection Rules:**
1. Focus on "safety" narrative vs. government inference API duality
2. Trace Schmidt influence through funding AND governance
3. Document Constitutional AI as regulatory moat mechanism
4. Map NAIAC representation (Dario Amodei member)
5. Verify Claude Gov classification levels and agency deployments

**Key Hypothesis:** Anthropic is not "controlled opposition" but an active chokepoint (betweenness: 0.1090) in the governance-to-intelligence path.

---

### LANE B: SCALE AI/RL (The Hidden Alignment Layer)

**Primary Targets:**
- Alexandr Wang (CEO)
- Scale AI government contracts (SAM.gov)
- Donovan platform (DoD deployments)
- Maven Smart System (RLHF labeling)
- Founders Fund investment terms

**Collection Rules:**
1. Document RLHF pipeline control over military AI targets
2. Trace Wang's personal connections to Thiel network
3. Verify Founders Fund investment and governance rights
4. Map Scale's data access agreements with OpenAI/Anthropic
5. Identify RLHF annotators for defense contracts


---

### LANE C: ORACLE INFRASTRUCTURE (The Invisible Monopolist)

**Primary Targets:**
- Larry Ellison (Chairman/CTO)
- Oracle Cloud Infrastructure (IC)
- JWCC contract (1 of 4 awardees)
- Project Stargate (co-investor)
- CIA/NSA backend operations

**Collection Rules:**
1. Force-collect Ellison->Oracle->JWCC/CIA/NSA chain (underrepresented in corpus)
2. Document nuclear data center concepts
3. Trace Oracle as compute substrate for Stargate
4. Map CIA cloud contracts and task orders
5. Verify Ellison-Schmidt-Thiel convergence points



---

## 3. AGENT PROMPTS (Copy-Paste Ready)

### AGENT A: ANTHROPIC LANE PROMPT

```
MISSION OBJECTIVE:
Expand adjacency matrix edges for Anthropic AI as a dual-use regulatory capture vehicle. 
Target: Dario/Daniela Amodei, Eric Schmidt, Google/Alphabet, AWS, Claude Gov.
Context: Claude Gov ranks #9 by betweenness (0.1090) - emerging broker node.

5 COLLECTION QUESTIONS TO ANSWER:
1. What is the complete Anthropic cap table from Series A to latest, with special attention to Schmidt's personal investment amount and any board representation?
2. Which specific agencies have deployed Claude Gov, at what classification levels, and for what mission sets?
3. How does Anthropic's Responsible Scaling Policy (RSP) compare to OpenAI's Preparedness Framework - are they converging or diverging?
4. What are the exact terms of Google's $2B+ investment and Amazon's $4B AWS partnership - governance rights, compute access, data sharing?
5. Who are the specific individuals representing Anthropic on NAIAC and what is their voting/policy influence?
6. What are the key differences between Anthropic's RSP and OpenAI's Preparedness Framework, and how do these differences impact their respective regulatory capture strategies?
OUTPUT FORMAT TEMPLATE (see Section 4):
Use 8-field standard output format for EACH finding.

RELATIONSHIP TAXONOMY FOR THIS LANE:
- OWN: Amodei siblings (founders)
- INV: Schmidt (Series A), Google/Alphabet ($2B+), Amazon/AWS ($4B)
- CON: Claude Gov contracts (identify agencies)
- PER: NAIAC representatives
- GOV: RSP policy influence, NSCAI recommendations
- PAR: AWS partnership terms
- DEP: Compute dependencies on AWS/Google

CONFIDENCE SCORING GUIDANCE:
- 1.00: Confirmed via SEC filings, Anthropic blog posts, or official gov announcements
- 0.95-0.99: Multi-source tech journalism corroboration
- 0.90-0.94: Single credible source (TechCrunch, The Information, etc.)
- 0.80-0.89: LinkedIn analysis, inference from partnership announcements
- Below 0.80: Mark as ASSESSMENT only, requires verification

PRIORITY FLAGS:
- [P1] Schmidt's exact investment amount and board seat status
- [P2] Claude Gov agency deployment list
- [P3] RSP vs OpenAI convergence evidence
```


---

### AGENT B: SCALE AI/RL LANE PROMPT

```
MISSION OBJECTIVE:
Illuminate Scale AI's structural invisibility while documenting its role as the DoD data labeling backbone.
Target: Alexandr Wang, Scale AI contracts, Donovan platform, Maven Smart System, RLHF pipeline.
Context: Scale AI is the "Hidden Alignment Layer" - controls what military AI learns is "correct."

5 COLLECTION QUESTIONS TO ANSWER:
1. What are Scale AI's complete government contracts (SAM.gov, USASpending) - values, agencies, and contract vehicles?
2. What are the exact terms of Founders Fund investment in Scale AI - amount, governance rights, board representation?
3. Which specific DoD programs use Scale's RLHF pipeline (Maven Smart System, Donovan, others)?
4. Who are the RLHF annotators for defense contracts - contractors, locations, clearance levels?
5. What are Scale's data access agreements with OpenAI and Anthropic - does Scale see training data?

MCP TOOL WORKFLOW (from workflows.md Section 5.2):
Step 1 - Search:
  bb7_search_web(query="Scale AI government contracts SAM.gov USASpending DoD", num_results=10)
  bb7_search_web(query="Founders Fund Scale AI investment Alexandr Wang Thiel", num_results=10)
  bb7_search_web(query="Scale AI Donovan platform Maven Smart System RLHF", num_results=10)

Step 2 - Fetch & Extract:
  bb7_fetch_url(url="[SAM.gov or USASpending contract record]", timeout=30)
  bb7_fetch_url(url="[Founders Fund portfolio or Scale AI press release]", timeout=30)

Step 3 - Store Findings:
  bb7_memory_store(
    key="scale-ai-dod-contracts-2026-02-18",
    value="[extracted contract values and agencies]",
    category="lane_b_findings",
    importance=0.95,
    tags=["scale-ai", "dod", "rlhf", "wang", "founders-fund"]
  )

OUTPUT FORMAT TEMPLATE (see Section 4):
Use 8-field standard output format for EACH finding.

RELATIONSHIP TAXONOMY FOR THIS LANE:
- OWN: Alexandr Wang (CEO)
- INV: Founders Fund (Thiel network - CRITICAL to verify)
- CON: Maven Smart System, Donovan platform contracts
- PER: Scale AI staff embedded at DoD locations (if any)
- GOV: RLHF policy influence (controls target definitions)
- PAR: OpenAI data partnership, Anthropic data partnership
- DEP: DoD dependency on Scale for RLHF pipeline

CONFIDENCE SCORING GUIDANCE:
- 1.00: SAM.gov contract records, official DoD announcements
- 0.95-0.99: Bloomberg Government, GovWin paid databases
- 0.90-0.94: Tech journalism with named sources
- 0.80-0.89: LinkedIn analysis, job postings for defense RLHF roles
- Below 0.80: Mark as ASSESSMENT only

PRIORITY FLAGS:
- [P1] Founders Fund investment confirmation and terms
- [P2] Maven Smart System Scale AI contract details
- [P3] Wang Thiel Fellowship status confirmation
```


---

### AGENT C: ORACLE LANE PROMPT

```
MISSION OBJECTIVE:
FORCE-COLLECT the Ellison->Oracle->JWCC/CIA/NSA chain. Ellison is underrepresented in corpus but is the Stargate compute substrate.
Target: Larry Ellison, Oracle Cloud Infrastructure, JWCC, CIA/NSA backends, Project Stargate.
Context: Ellison is the "invisible monopolist" - lowest doc frequency, highest structural centrality.

5 COLLECTION QUESTIONS TO ANSWER:
1. What are the specific Oracle JWCC task orders - which agencies, what mission sets, what dollar values?
2. What is the exact nature of Oracle's CIA cloud contract - when established, what's hosted, classification levels?
3. What is Ellison's specific role in Project Stargate - investment amount, infrastructure commitments, nuclear data center plans?
4. What NSA databases/systems run on Oracle infrastructure - documented via contracts or procurement records?
5. What is the Ellison-Schmidt-Thiel convergence - documented meetings, mutual investments, shared board positions?

MCP TOOL WORKFLOW (from workflows.md Section 5.2):
Step 1 - Search:
  bb7_search_web(query="Oracle JWCC task order award DoD CIO", num_results=10)
  bb7_search_web(query="Oracle CIA cloud contract intelligence community", num_results=10)
  bb7_search_web(query="Larry Ellison Project Stargate investment nuclear data center", num_results=10)
  bb7_search_web(query="Oracle NSA database contract infrastructure", num_results=10)

Step 2 - Fetch & Extract:
  bb7_fetch_url(url="[USASpending.gov or DoD CIO announcement]", timeout=30)
  bb7_fetch_url(url="[Oracle press release or SEC filing]", timeout=30)
  bb7_fetch_url(url="[Stargate announcement or infrastructure report]", timeout=30)

Step 3 - Store Findings:
  bb7_memory_store(
    key="oracle-jwcc-task-orders-2026-02-18",
    value="[extracted task order details]",
    category="lane_c_findings",
    importance=0.95,
    tags=["oracle", "ellison", "jwcc", "cia", "nsa", "stargate"]
  )

OUTPUT FORMAT TEMPLATE (see Section 4):
Use 8-field standard output format for EACH finding.

RELATIONSHIP TAXONOMY FOR THIS LANE:
- OWN: Larry Ellison (Chairman/CTO)
- INV: Project Stargate (co-investor with Altman)
- CON: JWCC (1 of 4 awardees), CIA cloud contracts
- PER: Oracle staff embedded at IC agencies
- GOV: IC AI governance via hosted infrastructure
- PAR: Palantir backend dependency (Oracle infrastructure for Foundry)
- DEP: Stargate dependency on Oracle compute

FORCE-COLLECT REQUIREMENTS:
This lane is UNDERREPRESENTED in current corpus. You MUST:
1. Create edges even with single-source evidence
2. Flag all findings with confidence <0.90 for verification
3. Search for alternative aliases ("Larry Ellison", "Oracle Corp", "Oracle Cloud", "Oracle IC")
4. Cross-reference with [U11] Oracle Origins doc in citation index

CONFIDENCE SCORING GUIDANCE:
- 1.00: USASpending.gov contract records, official DoD/IC announcements
- 0.95-0.99: Bloomberg, Reuters, WSJ with named government sources
- 0.90-0.94: Oracle press releases, earnings call transcripts
- 0.80-0.89: Tech journalism, LinkedIn analysis
- Below 0.80: Mark as ASSESSMENT ONLY - high priority for verification

PRIORITY FLAGS:
- [P1] JWCC Oracle task order specifics (agency, mission, value)
- [P2] CIA cloud contract establishment date and scope
- [P3] Ellison Stargate investment amount and infrastructure role
- [P4] Ellison-Schmidt-Thiel documented convergence
```


---

## 4. STANDARD OUTPUT TEMPLATE

Every finding MUST be output in this 8-field format:

```json
{
  "finding_id": "F-[LANE]-[YYYYMMDD]-[NNN]",
  "actor": "Entity name (person or organization)",
  "system": "System/Platform/Program name",
  "relationship": "OWN|INV|CON|PER|GOV|PAR|DEP",
  "cew_score": 0.00,
  "confidence": 0.00,
  "evidence_refs": ["[DocID:citation]", "[DocID:citation]"],
  "finding_summary": "One-sentence claim backed by evidence"
}
```

### Field Definitions:

| Field | Description | Example |
|-------|-------------|---------|
| `finding_id` | Unique identifier | F-A-20260218-001 |
| `actor` | Source entity | "Eric Schmidt" |
| `system` | Target entity | "Anthropic" |
| `relationship` | Relationship type code | "INV" |
| `cew_score` | Composite Edge Weight (calculated) | 0.85 |
| `confidence` | Authentication confidence (0-1) | 0.95 |
| `evidence_refs` | Array of [DocID:citation] | ["T22:15", "G01:8"] |
| `finding_summary` | Verifiable claim | "Schmidt invested $X in Anthropic Series A per SEC filing" |


---

## 5. RELATIONSHIP TAXONOMY REFERENCE

| Code | Relationship Type | Base Weight | Definition | Example |
|------|-------------------|-------------|------------|---------|
| **OWN** | Ownership / Founder | 1.00 | Direct corporate ownership, founding role, or controlling interest | Ellison owns Oracle; Thiel co-founded Palantir |
| **INV** | Investor | 0.80 | Venture capital, private equity, or sovereign wealth fund investment | Founders Fund invested in Anduril |
| **CON** | Contract Authority | 0.90 | Prime contractor, subcontractor, or sole-source provider via government award | Palantir holds Maven contract |
| **PER** | Personnel Placement | 0.75 | Board seat, advisory role, embedded staff, or revolving-door appointment | Thiel network alumni at DOGE |
| **GOV** | Governance / Policy | 0.85 | Chairmanship, regulatory authorship, or policy-setting role | Schmidt chaired NSCAI |
| **PAR** | Partnership / Alliance | 0.70 | Formal strategic partnership, joint venture, or MOA | OpenAI-Anduril partnership |
| **DEP** | Dependency | 0.65 | Infrastructure, compute, or data dependency (e.g., cloud backend) | Palantir Foundry on Oracle Cloud |


---

## 6. MERGE PROTOCOL

### 4-Step Integration Process

**STEP 1: Evidence Validation**
- Cross-reference all `evidence_refs` against `CITATION_INDEX.md`
- Verify document IDs exist and citations are valid
- Flag any [DocID:citation] that cannot be verified

**STEP 2: Normalization**
- Standardize actor names against known aliases in `entity_network.md`
- Standardize system names against `network_metrics.json`
- Merge duplicate actor-system-relationship tuples

**STEP 3: CEW Calculation**
```
CEW = sum(Base_Weight_i * Evidence_Multiplier_i) / N_max
```
- Apply base weight from relationship taxonomy
- Evidence Multiplier = Authentication Confidence Score
- Normalize to [0, 1]

**STEP 4: Adjacency Matrix Update**
- Append new edges to `data/derived/actor_system_edges_2026-02-18.json`
- Update `analysis/actor_system_adjacency_matrix.md` with new rows
- Regenerate overlap analysis for shared systems
- Publish updated matrix memo date-stamped in `analysis/`


---

## 7. CEW SCORING REFERENCE

### Composite Edge Weight Formula

```
CEW = sum(Base_Weight_i * Evidence_Multiplier_i) / N_max
```

Where:
- `Base_Weight_i` = Relationship type weight (from Section 5 taxonomy)
- `Evidence_Multiplier_i` = Authentication confidence of source
- `N_max` = Normalization factor (typically 1.0 for single-source, aggregated for multi-source)

### ARS Interpretation Bands

| ARS Range | Interpretation | Operational Significance |
|-----------|----------------|--------------------------|
| **1.00** | Direct ownership + operational control | Actor controls system completely |
| **0.90-0.99** | Contract prime / co-ownership / founding investment | Actor has primary control mechanism |
| **0.80-0.89** | Major investment + strategic partnership | Actor has significant influence |
| **0.70-0.79** | Governance role + policy influence | Actor shapes rules and access |
| **0.50-0.69** | Secondary linkage | Actor has indirect influence |
| **0.30-0.49** | Tertiary / inferred linkage | Contextual association only |
| **< 0.30** | Contextual only | No confirmed operational linkage |

### Confidence Scoring Reference

| Score | Source Type | Examples |
|-------|-------------|----------|
| 1.00 | Declassified primary docs, official releases | USASpending.gov, SEC filings, official statements |
| 0.95-0.99 | Multi-source triangulation | Leaked docs + journalism + corporate filings |
| 0.90-0.94 | Official corporate/government pubs | Press releases, earnings calls, procurement records |
| 0.80-0.89 | Credible independent reporting | Bloomberg, Reuters, WSJ with sources |
| < 0.80 | Inference, structural analysis | LinkedIn, job postings, pattern recognition |


---

## APPENDIX A: Quick Reference Card

| Task | Primary Tools |
|------|---------------|
| Search | `bb7_search_web` -> `bb7_fetch_url` |
| Store | `bb7_memory_store` with category="lane_[a|b|c]_findings" |
| Retrieve | `bb7_memory_retrieve` or `bb7_memory_search` |
| Validate | Cross-reference `CITATION_INDEX.md` |
| Calculate | Apply CEW formula from Section 7 |
| Output | Use 8-field JSON template from Section 4 |

---

## APPENDIX B: Lane-Specific Document IDs

### Lane A (Anthropic) Primary Sources:
- T22: Anthropic AI_ Origins and Network.md
- G01/G02: Anthropic's Global AI Governance
- T10: Deep State AI Governance OSINT.md
- U17: Anthropic Response to OSTP RFI (March 2025).pdf

### Lane B (Scale AI) Primary Sources:
- T08: Military AI Systems Intelligence Report.md (Maven references)
- T55: Thiel Defense Network Investigation_.md
- T06: Military AI Leak Investigation.md

### Lane C (Oracle) Primary Sources:
- U11: Oracle Origins_ Intelligence, Databases, and Cold .md
- T40: Stargate Program OSINT Deep Dive.md
- T10: Deep State AI Governance OSINT.md (JWCC)

---

## APPENDIX C: Workflows.md Section 5.2 Reference

Base operational pattern for all agents (Web Research Workflow):

```python
# 5.2 Fetch and Extract Content (workflows.md)

# Fetch page content
bb7_fetch_url(
    url="https://docs.example.com/api-reference",
    timeout=30
)

# Check URL status
bb7_check_url_status(
    url="https://api.example.com/health"
)

# Extract all links for crawling
bb7_extract_links(
    url="https://example.com/blog"
)
```

Complete workflow chain:
```python
# 1. Search for information
bb7_search_web(
    query="python asyncio best practices 2024",
    num_results=5
)

# 2. Fetch top results
bb7_fetch_url(url="https://stackoverflow.com/questions/...")
bb7_fetch_url(url="https://docs.python.org/...")

# 3. Store research
bb7_memory_store(
    key="research-async-orm",
    value="SQLAlchemy 2.0 supports async natively",
    category="research",
    importance=0.9
)
```

---

**END OF MOBILE RESEARCH GUIDE**

*Generated: 2026-02-18*  
*For operational use by Sovereign OSINT Deep-Search Agents*

**Document Path:** `docs/MOBILE_RESEARCH_GUIDE_2026-02-18.md`
