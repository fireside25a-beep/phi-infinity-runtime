# Contribution review matrix — evidence, boundaries and precise claims

| Component | Original issue | Proposed change | Evidence | Cannot claim |
|---|---|---|---|---|
| Gate transitions | No direct gate tests | Five frozen-state regression | `tests/test_gate_independent_audit.py` | Source authentication |
| Predicate failure | Unexpected exceptions did not lock | Fail-closed evaluation | `tests/test_gate_predicate_fail_closed.py` | That support was physically absent |
| Native real effect | No gate call site | Opt-in, serialized authorization of `engine.step()` | `tests/test_authorized_real_effects.py` | Prevent raw `.S`/`.R` writes |
| Boundary real effect | Separate mutating route | Same opt-in guard on `step_with_boundary()` | Exact state refusal and parity tests | That all possible Python callers are guarded |
| Check/effect race | Fresh read alone leaves a gap | Shared lock holds across real effect | Deterministic two-thread test | External atomicity across processes or physical world |
| Multi-language oracle | Only Python gate semantics | Independent C11 bounded state machine, 5120 decisions | `tests/test_c11_gate_oracle.py` | Proof of the M theory |
| Numerical behavior | No new physics permitted | Original mechanics untouched | Bit-exact state/result parity on tested cases | Formal global equivalence |

## Source review locations

`src/gating.py` stays the only definition of FirstDivergence and REOPEN.
`src/effect_authorization.py` owns the optional support transaction contract.
`src/core.py` and `src/boundary.py` gain only the authorization hook, not a
second state transition implementation.

## No hidden compatibility claim

- Normal, unattached engines remain ungated by design.
- `SynchronizedSupport.publish()` serializes competing *cooperative threads*.
- An out-of-band external change still can invalidate support after capture.
- `trigger_reopen()` does not itself validate interval independence.
- Direct updates to engine public arrays and calls to private mechanics remain
  possible and outside this feature's documented public entry-point contract.
- Error recovery from a midway mathematical exception is not a numerical
  rollback contract.
- Archived C11 tester check totals exercise C11 algorithms, not PHI mechanics.

Nothing in this contribution claims a completed physical implementation of M.
