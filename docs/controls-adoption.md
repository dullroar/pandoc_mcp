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

## Secret guard exceptions

none
