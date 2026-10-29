# Agent operating instructions — Ghostty Pets

## Mission

Implement the approved design in `docs/PRODUCT_SPEC.md`, constrained by `docs/ARCHITECTURE.md` and accepted ADRs, **one milestone at a time**.

## Required workflow

1. Read `README.md`, `docs/PRODUCT_SPEC.md`, `docs/ARCHITECTURE.md`, `docs/DELIVERY_PLAN.md`, and all ADRs before proposing work.
2. List material unknowns and any discrepancy between the spec and actual Ghostty behavior. **Ask rather than silently invent product decisions** when the choice affects UX, compatibility, dependencies, or scope.
3. For each milestone: propose a brief plan, identify the test/evidence, implement only that milestone, run available checks, then report results and explicitly **stop for human approval**.
4. Never start M(n+1) without explicit approval after M(n). In particular, M1 must be a narrow feasibility proof; do not create the full corgi art pack or behavior engine during M1.
5. Keep ADRs current. For substantive architecture changes, draft a new ADR before changing implementation. Do not overwrite accepted history; use a superseding ADR.
6. Keep a concise decision log and verification evidence in the milestone report. Explicitly distinguish verified, inferred, and untested claims.
7. Do not add a runtime service, installer, network access, shell hooks, native overlays, external image dependencies, or alternative rendering mechanisms without approval.
8. Always preserve a working Ghostty fallback: removing the `custom-shader` line disables the project.
9. Never promise or claim macOS/Linux manual validation that was not actually performed. Provide an exact human test checklist for unavailable platforms.

## Engineering standards

- Prefer simple readable Python + Pillow build tooling; pin dependencies, make output reproducible, and test transformations without requiring Ghostty.
- Source art remains editable PNG; data formats must be documented and validated.
- Generated GLSL is a release artifact, not the hand-edited source of truth.
- Profile shader compilation and rendering; avoid unbounded loops, huge source expansion and runtime texture uploads.
- Preserve terminal pixels outside the scene exactly (subject to texture-sampling precision), and prioritize readability over pet visibility.
- Keep per-surface rendering deterministic. Do not make frame-to-frame correctness depend on `iFrame` or continuously updating state.
- Favor explicit gates and measured trade-offs over premature abstractions.

## Initial assignment

Follow `CODEX_START.md`. Implement **M1 only**, after a brief proposed plan; conclude with evidence and unresolved questions. Do not proceed to M2 automatically.
