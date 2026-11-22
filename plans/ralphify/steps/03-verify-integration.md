---
id: 03-verify-integration
status: pending
depends_on: [02-build-and-test]
touches:
  - plans/ralphify/steps/03-verify-integration.md
lane: none
requirements: [R3]
gate: python3 scripts/check_context.py && bash scripts/test_docker.sh && git diff --check
evidence: ""
---

# 03-verify-integration

Depends on `02-build-and-test`. Update only the step file. Rerun the context and Docker gate from the integrated worktree as the driver would. Check the template and runner links in `AGENTS.md` and the structural-change rule. Verify README commands and the existing entry points. Record the worktree base commit, exact commands, build result, test counts or concrete smoke assertions, expected opt-in skips, real FUSE result where required, and UTC date. Keep logs outside Git. Gate: `python3 scripts/check_context.py && bash scripts/test_docker.sh && git diff --check`.

The driver writes its own `evidence` field. Put detailed test evidence in the body of the verification step and commit it. The parent verifies the final child commit and result. A green build alone cannot satisfy R2 or R3.

## Repository gate

Install Pandoc and the existing Python requirements. Add a stdio test under `tests/` that initializes, lists tools and formats, and converts an inline fixture to a different format. Assert actual converted content. Keep the documented stdio host entry point and any optional format requirements. Use local files for file conversion tests.

Run `git merge-base HEAD plan/ralphify` to identify the integrated base commit. Replace each pending value in the results below. For each passing check, put details after `PASS`. Include the actual Docker commands or image reference and test counts or concrete smoke results. Record `n/a` in the FUSE field for other repos. If a required test fails or skips, record that in resume notes and leave the result pending.

## Results

- Base commit: `52c243d440b7590117172b30b6983e678347731e` from `git merge-base HEAD plan/ralphify`.
- Commands: PASS. `python3 scripts/check_context.py && bash scripts/test_docker.sh && git diff --check`
  returned exit code 0. The sandbox denied access to the Docker socket. The same gate passed with
  local Docker access.
- Docker build: PASS. The gate built `pandoc-mcp-test:ujEjHnVt` from the worktree snapshot and ran
  it with `--network none`. The README build also passed with
  `docker build --tag pandoc-mcp-readme:AVrydYrN .`. The README image contained Pandoc 3.1.3 and
  MCP SDK 1.30.0. Its default command was `python server.py` and its user was `pandoc-mcp`.
- Tests: PASS. `python -m unittest discover -s tests -v` ran one test. It initialized an MCP stdio
  session, found both tools, found Markdown input and HTML5 output, and checked the exact HTML for
  an inline Markdown fixture and a local Markdown file. The four context checks passed on the
  host and inside Docker. The Git whitespace check passed.
- Skips: None. The gate requires no opt-in tests. PDF output can require a separate PDF engine,
  as the README states.
- FUSE: n/a.
- UTC date: 2026-11-22.

## Documentation and entry points

- PASS. Both upstream links in `AGENTS.md` returned HTTP 200. The structural-change rule requires
  agents to read both projects and account for their layout, plan format, generated indexes,
  worktree rules and validation commands.
- PASS. The README Docker test command ran in the gate. In the README image,
  `python server.py --help` confirmed the stdio default and the SSE, host and port options.
  The stdio test launched the documented Python entry point.
- The README command `ralph-looper --repo . --plan ralphify --agent codex` matched the runner's
  documented options. A separate `--status` invocation from the child worktree could not create
  its runtime directory or open the plan branch, which was already in use by the driver's plan
  worktree. The running driver owns the plan invocation and final verification.
