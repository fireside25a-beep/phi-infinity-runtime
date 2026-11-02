# MacBook manual fork/PR workflow (no direct access to canonical repo)

The source-only ZIP contains `PATCHES_FOR_MAC/`,
`CUMULATIVE_CHANGED_FILES_ONLY/` and `docs/` for review. The patches are
**cumulative stages**: each patch expects the previous stage applied, and
patch 01 expects the exact frozen upstream tree
`4ee4ea34b5b83cccff3463fec607c7ec0e10cd2a`.

The build was prepared against the user-provided ZIP named after that SHA,
not against an authenticated signed Git checkout. Before applying patches,
confirm the repository checkout really contains the expected starting blobs.

## On a clean fork checkout

1. In Terminal, go to your *own fork* clone, not the maintainer's repo.
2. Confirm `git status --short` is empty and run `git rev-parse HEAD`.
3. If upstream has not moved, start at the frozen target or maintainer-agreed
   merge base. Do not overwrite an existing worktree.
4. Make a new branch based on the frozen ref, **apply only stage 01**, run
   `python3 -m pytest -q`, commit, push to your fork, and open PR 01.
5. Once stage 01 is merged, start the next branch based on that merged target
   and apply stage 02; repeat for stages 03, 04 and 05. If PRs are stacked,
   make clear each review target is the preceding branch, not the frozen main.
6. Never apply `CUMULATIVE_CHANGE.patch` on top of individual patches.

Examples (replace only your local paths and branch names):

```sh
# inside your already-cloned personal fork
 git status --short
 git rev-parse HEAD
 git switch -c alex/phi-gate-audit 4ee4ea34b5b83cccff3463fec607c7ec0e10cd2a
 git apply --check /path/to/PATCHES_FOR_MAC/01_independent_gate_audit.patch
 git apply /path/to/PATCHES_FOR_MAC/01_independent_gate_audit.patch
 python3 -m pytest -q
 git add tests/test_gate_independent_audit.py docs/validation/INDEPENDENT_GATE_AUDIT.md
 git commit -m "test: independent PHI multi-access gate audit"
```

For stage 02 onward, use `git apply --check` with the corresponding patch
before applying, always in order and on the appropriate branch. Review the
changed files (`git diff --check`, `git diff --stat`) before committing.

macOS needs Python plus NumPy, SciPy, pytest, and Xcode Command Line Tools
(`xcode-select --install`) for the optional C11 oracle compilation. Create
a virtual environment if your default Python is managed externally.
Do not confuse the local archive-import commit with the real upstream SHA.

The original target owner requested **initially a test-only PR**. Do not
combine PR 01 with source changes without their agreement.
