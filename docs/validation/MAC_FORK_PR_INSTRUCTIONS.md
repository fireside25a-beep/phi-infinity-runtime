# Manual MacBook pull request procedure — nine independent stages

**Upstream frozen target:** `4ee4ea34b5b83cccff3463fec607c7ec0e10cd2a`.
Your provided ZIP is the audited source. Its archive SHA-256 is recorded in
`STAGE_METADATA.json` in the offline release, and the patch application
must be checked against the *actual Git checkout* before opening any PR.

The maintainer requested a **test-only first PR**. Preserve that boundary:
stage 01 is tests+report only and deliberately documents the unintegrated
effect gap. Stages 02–09 are **separate review commits** and may be submitted
as stacked PRs or follow-up PRs with the maintainer's approval. Do not submit
all nine as the first PR without prior maintainer agreement.

## Stage order

| Patch | Stage scope |
|---|---|
| `01_independent_gate_audit.patch` | Independent gate transitions + original real-effect gap evidence (test-only) |
| `02_predicate_fail_closed.patch` | Error-to-FirstDivergence fail-closed behavior |
| `03_serialized_real_effect_integration.patch` | Support lock around real native+boundary state effects |
| `04_independent_c11_oracle.patch` | Independent 5,120-row C11 gate model |
| `05_review_docs_example.patch` | Original review matrix and runnable demonstration |
| `06_engine_state_transactions.patch` | Transaction snapshots, callback mutation rejection, mechanics rollback |
| `07_versioned_quorum_reopen.patch` | Fixed-rule multi-channel support, newer-publication REOPEN |
| `08_sealed_effect_and_c11_oracle.patch` | Closed native PHI profile + 38,880-row C11 reference model |
| `09_review_docs_and_example.patch` | Complete examples, reviews, and API/documentation index |

Every patch is generated from one **real local Git commit** against its
predecessor, with a SHA-256 file in `PATCHES_FOR_MAC`. The cumulative patch
is an **alternative**, not something to apply on top of the nine stages.
Do not include the local import commit (`1114592`) in a PR. It was created
only to represent the user-supplied ZIP and is **not** the public Git SHA.

## Terminal procedure in your already-cloned personal fork

First, ensure your own fork's local checkout is clean. Installing tools:

```bash
xcode-select --install                    # only if macOS tools are absent
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt pytest
```

From the folder containing the extracted offline contribution bundle, use
`MAC_HELPERS/apply_one_stage.sh /absolute/path/to/your/fork 01` to apply only
stage 01 after confirming the expected frozen base. This helper **does not
commit, push, open a PR, or change any remote**. It aborts if the working tree
has changes or if `git apply --check` fails. Review the resulting diff, run
`python3 -m pytest -q`, and make the manual commit yourself.

The helper expects each next patch against the preceding stage. For stacked
PRs, target the immediately preceding PR branch. For post-merge PRs, update
your branch to the reviewed new upstream base and verify patch applicability.
Upstream changes may require a reviewed rebase; never force a patch if its
context differs.

C11 models are optional at runtime but required for full independent test
coverage; Xcode's `clang` satisfies the C11 compiler condition. Without a
compiler the Python tests explicitly **skip** the native oracle comparisons.
Do not report skipped C11 checks as passing.

The offline package also provides source-only changed-file copies for manual
inspection. Those files are **not a substitute** for reviewing/applying the
Git patches in correct stage order.
