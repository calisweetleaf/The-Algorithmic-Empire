# STAGE 3 — MATRIX COMPUTE + OVERLAP ANALYSIS
**Run Date:** 2026-02-18 02:21
**Stage:** 3 of 4

---

## 1. GATE STATUS

| Criterion | Status |
|---|---|
| Edges computed | ✅ 42 |
| Overlap nodes found | ✅ 12 |
| Deterministic (stable row counts) | ✅ PASS |

---

## 2. FULL ACTOR-SYSTEM CEW/ARS MATRIX

ARS scale: 1.00=OWN  0.90-0.99=CON/prime  0.80-0.89=INV+partner  0.70-0.79=GOV  0.50-0.69=secondary  <0.50=inferred

| System | Layer | Thiel ARS | Ellison ARS | Schmidt ARS | Altman ARS |
|---|---|---|---|---|---|
| NSCAI | L3 | — | — | **1.00** (GOV) | — |
| Worldcoin / World ID | L4 | — | — | — | **1.00** (OWN) |
| Altius-600M/700M | L6 | **0.95** (INV) | — | — | — |
| Dive-LD | L6 | **0.95** (INV) | — | — | — |
| Fury CCA | L6 | **0.95** (INV) | — | — | — |
| Ghost-X | L6 | **0.95** (INV) | — | — | — |
| Palantir Titan | L2 | **0.95** (OWN+PAR) | — | — | — |
| Project Stargate | L5 | — | **0.95** (INV+DEP) | — | **1.00** (OWN) |
| Arsenal-1 | L6 | **0.90** (INV) | — | — | — |
| NGC2 | L2 | **0.85** (CON) | — | — | — |
| DOGE | L3 | **0.80** (DEP+PER) | — | — | — |
| IDF AI Targeting | L6 | — | — | — | **0.80** (DEP) |
| Anduril Lattice | L2 | **0.95** (INV) | — | — | **0.70** (PAR) |
| Project Maven (AWCFT) | L1 | **0.90** (CON) | — | — | **0.60** (PAR) |
| Palantir Foundry | L2 | **1.00** (OWN) | **0.55** (DEP) | — | — |
| CogSecCollab | L4 | — | — | **0.50** (GOV) | — |
| DARPA SABER | L1 | — | — | **0.45** (GOV) | — |
| JWCC | L5 | **0.50** (CON) | **0.95** (CON) | **0.55** (GOV) | **0.45** (DEP) |
| Azure OpenAI (IL6) | L5 | — | **0.40** (DEP) | — | **0.95** (PAR) |
| Oracle Cloud IC | L5 | **0.40** (INV) | **1.00** (OWN) | — | — |
| STONEGHOST | L5 | — | **0.35** (DEP) | — | — |
| DARPA Augmented Cog | L1 | — | — | **0.30** (GOV) | — |
| OpenAI Usage Policy | L3 | — | — | **0.30** (PAR) | **1.00** (OWN) |
| ICD 505 | L3 | — | **0.25** (GOV) | **0.55** (GOV) | — |
| Palantir Gotham | L2 | **1.00** (OWN) | — | **0.25** (PAR) | **0.55** (PAR) |
| NAIAC | L3 | — | — | **0.70** (GOV) | **0.20** (PAR) |
| OMB M-25-21 | L3 | — | **0.20** (GOV) | **0.60** (GOV) | — |

---

## 3. CONVERGENCE / OVERLAP NODES (≥2 actors)

| Rank | System | Actors | Actor Count | Sum ARS | Max ARS | Controlling Actor |
|---|---|---|---|---|---|---|
| 1 | **JWCC** | Peter Thiel=0.50  Larry Ellison=0.95  Eric Schmidt=0.55  Sam Altman=0.45 | 4 | 2.450 | 0.950 | Larry Ellison |
| 2 | **Palantir Gotham** | Peter Thiel=1.00  Eric Schmidt=0.25  Sam Altman=0.55 | 3 | 1.800 | 1.000 | Peter Thiel |
| 3 | **Project Stargate** | Larry Ellison=0.95  Sam Altman=1.00 | 2 | 1.950 | 1.000 | Sam Altman |
| 4 | **Anduril Lattice** | Peter Thiel=0.95  Sam Altman=0.70 | 2 | 1.650 | 0.950 | Peter Thiel |
| 5 | **Palantir Foundry** | Peter Thiel=1.00  Larry Ellison=0.55 | 2 | 1.550 | 1.000 | Peter Thiel |
| 6 | **Project Maven (AWCFT)** | Peter Thiel=0.90  Sam Altman=0.60 | 2 | 1.500 | 0.900 | Peter Thiel |
| 7 | **Oracle Cloud IC** | Peter Thiel=0.40  Larry Ellison=1.00 | 2 | 1.400 | 1.000 | Larry Ellison |
| 8 | **Azure OpenAI (IL6)** | Larry Ellison=0.40  Sam Altman=0.95 | 2 | 1.350 | 0.950 | Sam Altman |
| 9 | **OpenAI Usage Policy** | Eric Schmidt=0.30  Sam Altman=1.00 | 2 | 1.300 | 1.000 | Sam Altman |
| 10 | **NAIAC** | Eric Schmidt=0.70  Sam Altman=0.20 | 2 | 0.900 | 0.700 | Eric Schmidt |
| 11 | **ICD 505** | Larry Ellison=0.25  Eric Schmidt=0.55 | 2 | 0.800 | 0.550 | Eric Schmidt |
| 12 | **OMB M-25-21** | Larry Ellison=0.20  Eric Schmidt=0.60 | 2 | 0.800 | 0.600 | Eric Schmidt |

---

## 4. LIVE METRIC CROSS-REFERENCE FOR TOP CONVERGENCE NODES

| System | PageRank (live) | Betweenness (live) | Degree (live) | Community |
|---|---|---|---|---|
| JWCC | N/A | N/A | N/A | N/A |
| Palantir Gotham | 0.01635 | 0.17684 | 83 | 8 |
| Project Stargate | 0.00510 | 0.01327 | 25 | 239 |
| Anduril Lattice | 0.00648 | 0.01434 | 33 | 8 |
| Palantir Foundry | N/A | N/A | N/A | N/A |
| Project Maven (AWCFT) | 0.01106 | 0.13050 | 55 | 8 |
| Oracle Cloud IC | N/A | N/A | N/A | N/A |
| Azure OpenAI (IL6) | N/A | N/A | N/A | N/A |
| OpenAI Usage Policy | N/A | N/A | N/A | N/A |
| NAIAC | N/A | N/A | N/A | N/A |

---

## 5. STRUCTURAL FINDINGS

- **4-actor convergence nodes:** 1 — JWCC
- **3-actor convergence nodes:** 1
- **2-actor convergence nodes:** 10

### Thiel Footprint
- Systems with Thiel linkage: 14
- Layers covered: [1, 2, 3, 5, 6]
- Mean ARS: 0.861

### Ellison Footprint
- Systems with Ellison linkage: 8
- Layers covered: [2, 3, 5]
- Mean ARS: 0.581

### Schmidt Footprint
- Systems with Schmidt linkage: 10
- Layers covered: [1, 2, 3, 4, 5]
- Mean ARS: 0.520

### Altman Footprint
- Systems with Altman linkage: 10
- Layers covered: [1, 2, 3, 4, 5, 6]
- Mean ARS: 0.725

---

**[END STAGE 3]** Gate: PASS → proceed to Stage 4