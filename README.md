# Ghostty Pets 🐕

A tiny autonomous pixel-art pet living inside Ghostty, drawn by a self-contained GLSL post-processing shader.

**Status:** product design approved; implementation not started. **First release:** a tricolor Pembroke Welsh Corgi in a cozy backyard. Supported targets: Ghostty on macOS and Linux.

## Start here

1. Read `docs/PRODUCT_SPEC.md` for what to build.
2. Read `docs/ARCHITECTURE.md` and `docs/adr/` for how and why.
3. Read `docs/DELIVERY_PLAN.md` for phased validation and acceptance gates.
4. Open Codex in this repository; `AGENTS.md` constrains how the agent should proceed.
5. Use the prompt in `CODEX_START.md`. **Do not start with the complete feature set.**

The intended end-user installation is manual: copy one prebuilt `.glsl` file to the Ghostty config directory and add the `custom-shader` setting. Python is a build-time dependency only.

## Documentation

- [`docs/PRODUCT_SPEC.md`](docs/PRODUCT_SPEC.md) — frozen product scope, functional requirements, UX and non-goals.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — shader constraints, proposed architecture, asset format and algorithms.
- [`docs/DELIVERY_PLAN.md`](docs/DELIVERY_PLAN.md) — M1–M5 milestones, test matrices, review gates and release criteria.
- [`docs/adr/`](docs/adr/) — independently reviewable architecture decisions.

## Authoritative references

- Ghostty custom shaders and their uniforms: https://ghostty.org/docs/config/reference
- Ghostty config file locations and reload behavior: https://ghostty.org/docs/config

Technical assumptions must be rechecked against the **installed Ghostty version**, not only the online docs.
