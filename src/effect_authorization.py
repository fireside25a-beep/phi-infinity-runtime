"""Opt-in cooperative support/effect serialization for PHI-INFINITY.

This is *not* an authentication layer. All evidence, predicates, and mutators
remain caller-controlled. Atomicity is defined ONLY relative to other threads
that publish through the SAME SynchronizedSupport instance. It cannot stop a
physical input changing, another process, direct state writes, or a malicious
Python participant. In particular, REOPEN still does not prove an independent
interval. Existing PHI equations are never copied or reimplemented here.

Alex Moraru — independent runtime contribution, 2026.
"""

import copy
from contextlib import contextmanager
from functools import wraps
import threading

from src.gating import FirstDivergenceException, MultiAccessGating
from src.state_transaction import EngineStateTransaction


class SynchronizedSupport:
    """Cooperative in-process source of copied support observations.

    All cooperating publishers *must* use publish(). An effect holds the same
    lock from evidence capture through the native effect's return. This makes
    publish() wait until the effect completes, without simulating mechanics.
    """

    def __init__(self, initial_evidence):
        self._lock = threading.RLock()
        self._local = threading.local()
        self._evidence = copy.deepcopy(initial_evidence)

    def publish(self, evidence):
        """Replace evidence atomically; prevents reentrant publication in effect."""
        if getattr(self._local, 'inside_effect', False):
            raise RuntimeError('Cannot publish from inside an authorized effect')
        prepared = copy.deepcopy(evidence)
        with self._lock:
            self._evidence = prepared

    def snapshot(self):
        """Diagnostic copy only, NOT an authorization token."""
        with self._lock:
            return copy.deepcopy(self._evidence)

    @contextmanager
    def effect_window(self):
        """Yield fresh evidence while serializing all cooperative publications."""
        with self._lock:
            if getattr(self._local, 'inside_effect', False):
                raise RuntimeError('Recursive authorization on same support source')
            self._local.inside_effect = True
            try:
                yield copy.deepcopy(self._evidence)
            finally:
                self._local.inside_effect = False


class _EffectBinding:
    """One bound gate, one support source, and one serialized engine."""

    def __init__(self, gate, support):
        self.gate = gate
        self.support = support
        self.check_index = 0
        self.engine_lock = threading.RLock()


def attach_gate_to_engine(engine, gate, support):
    """Attach exactly once, without changing an engine's numerical state."""
    if not isinstance(gate, MultiAccessGating):
        raise TypeError('gate must be a MultiAccessGating')
    if not isinstance(support, SynchronizedSupport):
        raise TypeError('support must be a SynchronizedSupport')
    if getattr(gate, '_phi_required_source', support) is not support:
        raise ValueError('Versioned gate must use its bound support source')
    if getattr(engine, '_phi_effect_binding', None) is not None:
        raise RuntimeError('An effect gate is already attached')
    bound_owner = getattr(gate, '_phi_effect_owner', None)
    if bound_owner is not None and bound_owner is not engine:
        raise RuntimeError('This gate is already attached to another engine')
    engine._phi_effect_binding = _EffectBinding(gate, support)
    gate._phi_effect_owner = engine


def authorized_effect(func):
    """Serialize, authorize and transact one real public PHI state transition.

    The opt-in path snapshots every supported engine instance attribute before
    invoking the caller's predicate. A predicate mutation is rolled back and
    refused even if the predicate returns True. Mechanics exceptions likewise
    roll back and lock, rather than leaving a partly committed PHI state.
    """
    @wraps(func)
    def invoke(engine, *args, **kwargs):
        binding = getattr(engine, '_phi_effect_binding', None)
        if binding is None:
            return func(engine, *args, **kwargs)
        with binding.engine_lock:
            if binding.gate.execution_locked:
                raise FirstDivergenceException(
                    'System locked in FirstDivergence. REOPEN protocol required.'
                )
            entered = False
            txn = None
            try:
                with binding.support.effect_window() as metrics:
                    entered = True
                    # Fail closed if a subclass brings unsupported state. No
                    # incomplete snapshot can be mistaken for a transaction.
                    txn = EngineStateTransaction(engine, binding)
                    try:
                        binding.gate.check_trajectory(metrics, binding.check_index)
                    except BaseException:
                        binding.gate.execution_locked = True
                        txn.restore()
                        raise
                    if binding.gate.execution_locked:
                        txn.restore()
                        raise FirstDivergenceException(
                            '[FIRSTDIVERGENCE] Gate became locked during evaluation.'
                        )
                    if not txn.unchanged():
                        binding.gate.execution_locked = True
                        txn.restore()
                        raise FirstDivergenceException(
                            '[FIRSTDIVERGENCE] Acceptance predicate modified engine state.'
                        )
                    binding.check_index += 1
                    try:
                        result = func(engine, *args, **kwargs)
                    except BaseException:
                        binding.gate.execution_locked = True
                        txn.restore()
                        raise
                    return result
            except BaseException as exc:
                if not entered and not binding.gate.execution_locked:
                    binding.gate.execution_locked = True
                    raise FirstDivergenceException(
                        '[FIRSTDIVERGENCE] Could not acquire fresh support evidence.'
                    ) from exc
                if txn is None and not binding.gate.execution_locked:
                    binding.gate.execution_locked = True
                    raise FirstDivergenceException(
                        '[FIRSTDIVERGENCE] Engine state cannot be transacted safely.'
                    ) from exc
                raise
    return invoke
