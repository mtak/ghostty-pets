# ADR-0010 — Quiet animation clock independent of cursor changes

**Status:** Accepted for M3 after user validation feedback

**Context:** ADR-0009 removed global fading on cursor changes, but the Quiet episode clock was still measured from the latest cursor change. Each keypress that moved the terminal cursor therefore restarted the pet's Quiet animation at its first frame.

**Decision:** Use cursor-change age only to select Quiet, Active, or Sleeping mode. Evaluate Quiet episode slots and frames from time since the pane last gained focus, which continues across cursor changes. Active episodes continue to use the idle interval after the latest cursor/focus event so the first Active episode begins at home after 10 seconds. Focus gain can restart Quiet animation after the wake transition.

**Consequences:** Repeated typing leaves the in-place Quiet animation running. A switch from Active motion to Quiet can still recenter immediately, as accepted in ADR-0009. Quiet episode selection remains deterministic and per-surface, with no stored state or new Ghostty input dependency. This refines the Quiet time-base portion of ADR-0008; ADR-0009's steady-opacity policy remains in force.
