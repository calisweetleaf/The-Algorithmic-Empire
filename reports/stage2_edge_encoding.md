# STAGE 2 — EDGE ENCODING REPORT
**Run Date:** 2026-02-18 02:21
**Stage:** 2 of 4

---

## 1. GATE STATUS

| Criterion | Status |
|---|---|
| No undefined relationship codes | ✅ PASS |
| No duplicate actor-system-rel_type tuples | ✅ PASS |
| All actors use canonical names | ✅ PASS |

---

## 2. ALIAS NORMALIZATION

| Raw Alias | Canonical Name | Action |
|---|---|---|
| Thiel / Peter A. Thiel / Thiel Nexus | **Peter Thiel** | Merged (91 aliases resolved in entity_clean) |
| Oracle Corp / Oracle Corporation / Oracle Cloud | **Oracle Cloud IC** | Separate nodes retained — Ellison links to OWN node |
| Sam Altman / Samuel H. Altman | **Sam Altman** | Merged |
| Eric Schmidt / E. Schmidt / Google CEO | **Eric Schmidt** | NOT IN GRAPH — governance-only actor |
| Larry Ellison / Oracle Founder / Oracle Chairman | **Larry Ellison** | Merged; community=171 |
| Anduril Lattice OS / Lattice OS | **Anduril Lattice** | Unified for edge encoding |
| World ID / Worldcoin | **Worldcoin / World ID** | Unified |

---

## 3. RELATIONSHIP TYPE TAXONOMY

| Code | Type | Base Weight |
|---|---|---|
| **OWN** | Ownership/Founder | 1.00 |
| **CON** | Contract Authority | 0.90 |
| **GOV** | Governance/Policy | 0.85 |
| **INV** | Investor | 0.80 |
| **PER** | Personnel Placement | 0.75 |
| **PAR** | Partnership/Alliance | 0.70 |
| **DEP** | Dependency | 0.65 |

---

## 4. ENCODED EDGE TABLE

| Actor | System | Layer | Rel Types | Base Wt | EM | CEW | ARS | Confidence | Source Refs | Live CoOcc |
|---|---|---|---|---|---|---|---|---|---|---|
| Peter Thiel | Project Maven (AWCFT) | L1 | CON | 0.90 | 0.85 | 0.765 | 0.90 | HIGH | T14,T55,T08 | 0 |
| Peter Thiel | Palantir Gotham | L2 | OWN | 1.00 | 1.00 | 1.000 | 1.00 | VERIFIED | T17,T26 | 0 |
| Peter Thiel | Palantir Foundry | L2 | OWN | 1.00 | 1.00 | 1.000 | 1.00 | VERIFIED | T10 | 0 |
| Peter Thiel | Palantir Titan | L2 | OWN+PAR | 0.85 | 0.95 | 0.807 | 0.95 | HIGH | T55 | 0 |
| Peter Thiel | Anduril Lattice | L2 | INV | 0.80 | 0.90 | 0.720 | 0.95 | VERIFIED | T55,T11 | 0 |
| Peter Thiel | NGC2 | L2 | CON | 0.90 | 0.80 | 0.720 | 0.85 | HIGH | T56 | 0 |
| Peter Thiel | DOGE | L3 | DEP+PER | 0.70 | 0.75 | 0.525 | 0.80 | HIGH | T24,T10 | 0 |
| Peter Thiel | JWCC | L5 | CON | 0.90 | 0.50 | 0.450 | 0.50 | MEDIUM | T08 | 0 |
| Peter Thiel | Oracle Cloud IC | L5 | INV | 0.80 | 0.35 | 0.280 | 0.40 | LOW | T22 | 0 |
| Peter Thiel | Ghost-X | L6 | INV | 0.80 | 0.90 | 0.720 | 0.95 | VERIFIED | T55 | 0 |
| Peter Thiel | Altius-600M/700M | L6 | INV | 0.80 | 0.90 | 0.720 | 0.95 | HIGH | T56 | 0 |
| Peter Thiel | Dive-LD | L6 | INV | 0.80 | 0.90 | 0.720 | 0.95 | HIGH | T55 | 0 |
| Peter Thiel | Fury CCA | L6 | INV | 0.80 | 0.90 | 0.720 | 0.95 | HIGH | T56 | 0 |
| Peter Thiel | Arsenal-1 | L6 | INV | 0.80 | 0.85 | 0.680 | 0.90 | MEDIUM | T55,T56 | 0 |
| Larry Ellison | Oracle Cloud IC | L5 | OWN | 1.00 | 1.00 | 1.000 | 1.00 | VERIFIED | U11,T22 | 0 |
| Larry Ellison | JWCC | L5 | CON | 0.90 | 0.92 | 0.828 | 0.95 | VERIFIED | T40 | 0 |
| Larry Ellison | Project Stargate | L5 | INV+DEP | 0.72 | 0.92 | 0.667 | 0.95 | VERIFIED | T40 | 0 |
| Larry Ellison | Palantir Foundry | L2 | DEP | 0.65 | 0.50 | 0.325 | 0.55 | MEDIUM | T10 | 0 |
| Larry Ellison | Azure OpenAI (IL6) | L5 | DEP | 0.65 | 0.35 | 0.228 | 0.40 | LOW | T40 | 0 |
| Larry Ellison | STONEGHOST | L5 | DEP | 0.65 | 0.30 | 0.195 | 0.35 | LOW | U11 | 0 |
| Larry Ellison | ICD 505 | L3 | GOV | 0.85 | 0.20 | 0.170 | 0.25 | LOW | U11 | 0 |
| Larry Ellison | OMB M-25-21 | L3 | GOV | 0.85 | 0.18 | 0.153 | 0.20 | LOW | U11 | 0 |
| Eric Schmidt | NSCAI | L3 | GOV | 0.85 | 1.00 | 0.850 | 1.00 | VERIFIED | T10,T42 | 0 |
| Eric Schmidt | NAIAC | L3 | GOV | 0.85 | 0.65 | 0.552 | 0.70 | HIGH | T22,G01 | 0 |
| Eric Schmidt | JWCC | L5 | GOV | 0.85 | 0.50 | 0.425 | 0.55 | MEDIUM | T10 | 0 |
| Eric Schmidt | ICD 505 | L3 | GOV | 0.85 | 0.50 | 0.425 | 0.55 | MEDIUM | T42 | 0 |
| Eric Schmidt | OMB M-25-21 | L3 | GOV | 0.85 | 0.55 | 0.468 | 0.60 | MEDIUM | T42 | 0 |
| Eric Schmidt | CogSecCollab | L4 | GOV | 0.85 | 0.45 | 0.383 | 0.50 | MEDIUM | T42 | 0 |
| Eric Schmidt | DARPA SABER | L1 | GOV | 0.85 | 0.40 | 0.340 | 0.45 | LOW | T42 | 0 |
| Eric Schmidt | DARPA Augmented Cog | L1 | GOV | 0.85 | 0.25 | 0.212 | 0.30 | LOW | T42 | 0 |
| Eric Schmidt | OpenAI Usage Policy | L3 | PAR | 0.70 | 0.25 | 0.175 | 0.30 | LOW | T22 | 0 |
| Eric Schmidt | Palantir Gotham | L2 | PAR | 0.70 | 0.20 | 0.140 | 0.25 | LOW | T10 | 0 |
| Sam Altman | Project Stargate | L5 | OWN | 1.00 | 1.00 | 1.000 | 1.00 | VERIFIED | T40 | 9 |
| Sam Altman | OpenAI Usage Policy | L3 | OWN | 1.00 | 1.00 | 1.000 | 1.00 | VERIFIED | S05 | 0 |
| Sam Altman | Worldcoin / World ID | L4 | OWN | 1.00 | 1.00 | 1.000 | 1.00 | VERIFIED | O04,O05,O12 | 0 |
| Sam Altman | Azure OpenAI (IL6) | L5 | PAR | 0.70 | 0.92 | 0.644 | 0.95 | HIGH | T14,T32 | 0 |
| Sam Altman | IDF AI Targeting | L6 | DEP | 0.65 | 0.78 | 0.507 | 0.80 | HIGH | T25,T33 | 0 |
| Sam Altman | Anduril Lattice | L2 | PAR | 0.70 | 0.65 | 0.455 | 0.70 | HIGH | T28,T20 | 0 |
| Sam Altman | Project Maven (AWCFT) | L1 | PAR | 0.70 | 0.55 | 0.385 | 0.60 | MEDIUM | T08,S05 | 0 |
| Sam Altman | Palantir Gotham | L2 | PAR | 0.70 | 0.50 | 0.350 | 0.55 | MEDIUM | T28 | 0 |
| Sam Altman | JWCC | L5 | DEP | 0.65 | 0.40 | 0.260 | 0.45 | MEDIUM | T40,T32 | 0 |
| Sam Altman | NAIAC | L3 | PAR | 0.70 | 0.18 | 0.126 | 0.20 | LOW | G01 | 0 |

---

## 5. EDGE COUNTS BY ACTOR

| Actor | Edges | Layers Covered | Max ARS |
|---|---|---|---|
| Peter Thiel | 14 | [1, 2, 3, 5, 6] | 1.00 |
| Larry Ellison | 8 | [2, 3, 5] | 1.00 |
| Eric Schmidt | 10 | [1, 2, 3, 4, 5] | 1.00 |
| Sam Altman | 10 | [1, 2, 3, 4, 5, 6] | 1.00 |

---

**[END STAGE 2]** Gate: PASS → proceed to Stage 3