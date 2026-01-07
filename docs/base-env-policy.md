# Base Environment Policy (Opinionated)

Goal: keep base as the "orchestrator" layer.

Recommended base contents:
- conda + solver plugin(s) + auth/TLS chain
- a small set of packaging helpers if you build/publish frequently
- minimal shell integrations

Avoid in base:
- heavy runtime stacks (numpy/scipy/torch/etc.) unless you intentionally use base as a real dev env
- project-specific dependencies

Rationale:
- fewer conflicts
- easier recovery/upgrade
- clearer separation: base = control plane; envs = workloads
