# Role Execution Matrix

## Objective
Define how planner, builders, and finisher operate as one distributed execution system while preserving role specialization.

## Role Responsibilities
1. `planner_reasoner`
- Build architecture plan and phase contracts.
- Define dependency order and acceptance criteria.
- Produce execution harness prompts for builder agents.
- Review returned deltas and plan next stage.

2. `builder_executor`
- Implement assigned scope at high throughput.
- Return concrete file edits and verification evidence.
- Surface blockers with precise root causes.
- Never expand scope without updated stage contract.

3. `finisher_polisher`
- Merge and normalize cross-agent outputs.
- Resolve regressions and tighten operational hardening.
- Finalize docs, runbooks, and release quality checks.

## Stage Workflow
1. Planner emits stage contract.
2. Builder executes against contract.
3. Builder emits handoff packet matching `docs/HANDOFF_SCHEMA.json`.
4. Planner validates and emits next-stage contract.
5. Finisher runs after implementation waves converge.

## Mandatory State Writes Per Stage
1. Update `CONTEXT.md` with what changed and current status.
2. Update `MEMORY.md` with durable lessons and risks.
3. Update `docs/STATE_SNAPSHOT_<date>.md` if execution status changed.
4. Store BB7 memory entry keyed by stage and date.

## Exoskeleton Governance
Per major task, execute:
1. `bb7_exo_bootstrap`
2. `bb7_exo_list_tool_categories`
3. `bb7_exo_category_specific_tools`
4. `bb7_exo_route`
5. `bb7_exo_plan`
6. Execute selected tools
7. `bb7_exo_reflect`

## Coverage Rule
- Each stage must log which categories were considered.
- Tools are selected by intent fit.
- Unused categories are recorded in handoff packet and reviewed in next planning pass.

## Current Baseline Reference
- Use `docs/STATE_SNAPSHOT_2026-02-17.md` as initial baseline for this matrix rollout.
- Use `skills/bb7-distributed-cognition/bb7_manifest.json` as the canonical BB7 policy source for this repo.
