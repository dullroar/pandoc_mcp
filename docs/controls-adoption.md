---
gist: "Read me when: you change the pinned deterministic-controls library, the check_context.py shim, controls.toml or the controls CI job."
---

# Controls adoption

This repository runs the pinned `deterministic-controls` library in advisory mode. The `controls` CI job is not a required check yet.

## How it works

- `scripts/check_context.py` is a shim. It runs the library and prints one line for each old check (`ok  <script>` or `FAIL <script>`). It exits `0` on pass and `1` on defects.
- The pin is in `scripts/controls-requirements.txt`. It holds one install line with a full commit.
- The shim builds a virtual environment for the pinned commit. The cache path is `$XDG_CACHE_HOME/deterministic-controls/<commit>/`. The default is `~/.cache/deterministic-controls/<commit>/`.
- The first run for a commit needs the network. Later runs use the cache.
- If the library cannot run, the shim exits `2`. It never passes without a result. It never falls back to the old scripts.
- `controls.toml` selects the checks and the profile.
- The old check scripts stay in `scripts/`.

## How the adoption was made

1. Audit: step `a01-audit` wrote `docs/controls-audit.json`. The audit is read-only.
2. Plan: `adopt plan` made a dry run with the pinned commit. We read it.
3. Apply: `adopt apply` wrote the shim, the pin, `controls.toml` and the `controls` CI job. We then made the changes in the next section.

## Where the tools did not fit

- `adopt apply` rewrote `scripts/install_hooks.sh` (a `secretguard.path` fallback). That file is outside the scope of this step. We restored it from the previous commit.
- The pin file needed no `Run me when:` line. `apply` wrote one.
- The Docker run has no network, but the shim needs the network once for the pinned commit. We changed the `Dockerfile`. The image build now installs `git` and prepares the shim cache as user `pandoc-mcp`. The cache is under the home of that user. The container then runs `python scripts/check_context.py` with no network. `git` is also needed by `tests/test_secret_guard.py`.
- The Docker image was not built in this step, because the session cannot run Docker. The driver runs `bash scripts/test_docker.sh`.

## Probes

Date of all runs: 2026-11-24 (UTC). Each probe ran in a throwaway clone of `HEAD` under `.probe/`. The command was `python3 -m deterministic_controls check --root <copy> --profile ci --format json`. The real tree was not changed. `.probe/` was deleted before the gate.

| Probe | Expected rule ID | Exit code | Result |
| --- | --- | --- | --- |
| Broken relative link in a Markdown file | `markdown.local-links` | 1 | Failed with `markdown.local-links.missing-file`. |
| Stale generated index (script changed, index not rebuilt) | `context.index-freshness` | 1 | Failed with `context.index-freshness.stale`. |
| Plan step without `gate` | `plans.schema` | 1 | Failed with `plans.schema.missing-gate`. |
| Synthetic token in a committed Markdown file (built at run time) | `security.secrets` | 1 | Failed with `security.secrets.github-token`. `security.personal-data` also found the token. |
| Tracked `driver.out` file | `repo.forbidden-artifacts` | 1 | Failed with `repo.forbidden-artifacts.tracked`. |
| Internal error (Markdown file with no read permission) | none (the check must not pass) | 3 | Status `error` for `markdown.local-links` and `security.personal-data`. It did not pass. |
| Plan step without `gate`, run through the `scripts/check_context.py` shim | `plans.schema` | 1 | The shim printed `FAIL check_plan.py` and exited `1`. |

Each bad probe failed for the expected reason. After the read permission was restored, the copy passed (exit `0`). A clean clone of `HEAD` also passed (exit `0`).

## Rollback

Date of the test: 2026-11-24 (UTC).

Test result:

- The base commit is the parent of the `adopt apply` commit. In a clone under `.probe/`, its `python3 scripts/check_context.py` passed on the clean tree. All four old checks printed `ok`.
- The new shim passed on a clean clone of `HEAD`. It printed `ok` for the four old checks and for `repo.forbidden-artifacts`.

There is no earlier pin. To roll back, use one of these ways:

1. Change the pin. Edit `scripts/controls-requirements.txt`, put another commit in the install line, and run `python3 scripts/check_context.py` once. The run builds the environment for that commit.
2. Remove the adoption. Make a new branch. Run `git revert` on the adoption commits. Then run `python3 scripts/check_context.py`. It must pass with the old scripts.

Files of the adoption (the `adopt apply` commit):

- Added: `controls.toml`, `docs/controls-adoption.md`, `scripts/controls-requirements.txt`.
- Changed: `.github/workflows/context.yml`, `AGENTS.md`, `Dockerfile`, `docs/README.md`, `scripts/AGENTS.md`, `scripts/check_context.py`.
- Kept: the old check scripts in `scripts/`, `scripts/test_docker.sh`, the unit tests and the `check` CI job.

The cache under `$XDG_CACHE_HOME/deterministic-controls/<commit>/` is safe to delete. The shim builds it again when it needs it.

## Receipt

Date of the run: 2026-11-24 (UTC). Command: `python3 -m deterministic_controls adopt receipt --root <clean clone> --commit 3a2e9f3d95136958c54f73c831e84b971fc9a054`. It ran in a clean clone of `HEAD` under `.probe/`.

- `repository` is the name of the temporary clone, not of the project.
- `files_added` and `files_changed` are empty in a clean clone. This is a known library defect. The Rollback section lists the files of the adoption.
- `enforcement_state` is `advisory`.

```json
{
  "base_revision": "137752ce907e103fa8d9861c012f2d4837a5de6e",
  "checks_run": [
    {"check_id": "context.index-freshness", "status": "passed"},
    {"check_id": "markdown.local-links", "status": "passed"},
    {"check_id": "plans.graph", "status": "passed"},
    {"check_id": "plans.schema", "status": "passed"},
    {"check_id": "repo.forbidden-artifacts", "status": "passed"},
    {"check_id": "security.personal-data", "status": "passed"},
    {"check_id": "security.secrets", "status": "passed"}
  ],
  "commands_kept": [
    "scripts/build_context_indexes.py",
    "scripts/build_indexes.py",
    "scripts/check_links.py",
    "scripts/check_plan.py",
    "scripts/ctx_common.py",
    "scripts/scan_context_secrets.py",
    "scripts/scan_secrets.py",
    "scripts/test_docker.sh",
    "test: python3 -m unittest discover -s tests",
    "test: docker build (Dockerfile)",
    "ci-job: check"
  ],
  "control_pin": "3a2e9f3d95136958c54f73c831e84b971fc9a054",
  "date": "2026-11-24",
  "enabled_checks": [
    "context.index-freshness",
    "markdown.local-links",
    "plans.graph",
    "plans.schema",
    "repo.forbidden-artifacts",
    "security.personal-data",
    "security.secrets"
  ],
  "enforcement_state": "advisory",
  "files_added": [],
  "files_changed": [],
  "profile": "ci",
  "repository": "clean",
  "schema_version": 1
}
```

The receipt also has a `rollback` list. The Rollback section above replaces it.

## Secret guard exceptions

none
