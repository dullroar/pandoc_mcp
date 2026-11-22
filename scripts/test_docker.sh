#!/usr/bin/env bash
# Run me when: testing Pandoc conversion and context checks in Docker.
set -euo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
scratch=$(mktemp -d "${TMPDIR:-/tmp}/pandoc-mcp-test.XXXXXXXX")
run_id=${scratch##*.}
tag="pandoc-mcp-test:$run_id"
trap 'rm -rf -- "$scratch"' EXIT

# Use current file contents for Git-indexed paths. The snapshot contains no Git metadata.
git ls-files --cached --deduplicate -z |
    while IFS= read -r -d '' path; do
        if [[ -e "$path" || -L "$path" ]]; then
            printf '%s\0' "$path"
        fi
    done |
    tar --create --file "$scratch/source.tar" --no-recursion --null --files-from=-

docker build --tag "$tag" - < "$scratch/source.tar"
trap 'docker image rm "$tag" >/dev/null; rm -rf -- "$scratch"' EXIT

docker run --rm --network none --name "pandoc-mcp-test-$run_id" "$tag" bash -ec '
    python -m unittest discover -s tests -v
    python scripts/check_context.py
'
