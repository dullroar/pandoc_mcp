# Agent contract

An MCP-facing conversion boundary around Pandoc, via pypandoc.

## Standing rules

- Start work on a branch. Use a separate worktree for each plan and for each step that runs in
  parallel. Do not commit to `main`.
- Do not put credentials, personal data, personal paths, private host names or sensitive record
  examples in tracked files. Use placeholders and aggregate evidence. Keep runtime output outside
  the repository.
- Write in Simplified Technical English. Use short sentences, active voice and consistent terms.
- Do not push, publish, force-push or add a remote without authorization.
- Do not weaken the controls. You may run the local checks at any time. CI runs them in all cases.
  Do not change or disable the controls, the pin (`scripts/controls-requirements.txt`),
  `controls.toml` or the workflows to make an unrelated task pass. The driver checks the gate and
  `touches` of each step. A change to the gate or a file outside `touches` fails the step. Send each
  piece of work to the cheapest executor that can do it, and let the gate decide if the work is done.
  The full policy is at <https://github.com/dullroar/ralph-looper/blob/main/docs/routing.md>.
- User instructions come first. When sources conflict, use this order. Read this file before
  `docs/design/`, then the named plan, domain documentation and references, `memory/`,
  implementation and tests, and historical notes.

## Load context in this order

1. Read this file.
2. Read the short indexes in full. Start with [README.md](./README.md) and [docs/README.md](./docs/README.md).
   Then read [memory/AGENTS.md](./memory/AGENTS.md), [plans/AGENTS.md](./plans/AGENTS.md) and
   [scripts/AGENTS.md](./scripts/AGENTS.md).
3. Match the task to the **Read when**, **Read me when** and **Run me when** entries.
   Open only matching documents. For a large file, search its headings and read the relevant ranges.
4. Stop when you know the decision, files, constraints and validation method.

## Repository structure

Before changing this repository's structure, read [repo-template](https://github.com/dullroar/repo-template)
and [ralph-looper](https://github.com/dullroar/ralph-looper). Account for their layout, plan format,
generated indexes, worktree rules, and validation commands in the change.

| Path | Contents |
| --- | --- |
| `docs/` | Human documentation. Put architectural reasons in `docs/design/`, one premise per file. |
| `memory/` | Non-obvious findings that cost time to discover. Keep one file per topic. Edit the existing topic. |
| `plans/` | Plan requirements, steps and execution state. |
| `scripts/` | Deterministic automation for agents and CI. |

Keep each fact in its source file. Routed Markdown starts with a `gist` in front matter.
Each script starts with a **Run me when** line. Run `python3 scripts/build_indexes.py` after changes
to routed files. Edit the generated sections through the script.

## Planned work

- Work on a named plan or an explicitly identified off-plan task. Copy
  [plans/for-each-plan/](./plans/for-each-plan/) to start a plan.
- Approve the requirements and protected checks in `spec.md` before execution. Proceed through the
  approved steps without asking for routine decisions. Diagnose and fix failures within scope.
- Escalate contradictions, scope changes, actions outside delegated authority and protected checks
  that cannot pass as written. Never weaken, skip or delete a protected check to make it pass.
- Run steps in parallel only when there is no dependency and their `touches` do not overlap.
  If independence is uncertain, run the steps in order. After parallel steps merge, run the combined
  validation in the spec.
- Record evidence before you mark a step complete. Report unavailable verification in the step.
- Record the type of rule change. Distinguish rule retirement, documentation correction and a
  tolerated violation. See the [spec template](./plans/for-each-plan/spec.md#exceptions-and-retirements).

## Validation

Run the smallest check that proves the change. For a context change, run
`python3 scripts/check_context.py`.
