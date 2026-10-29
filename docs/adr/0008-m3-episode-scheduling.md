# ADR-0008 — Bounded stateless animation episodes

**Status:** Accepted for the approved M3 implementation

**Context:** Ghostty supplies time, latest cursor-change time, and focus, but no persistent shader state, keyboard events, or stable pane identifier. A cursor event can invalidate the previous mode and movement trajectory while the pet is mid-walk.

**Decision:** Compile versioned PNG/JSON animation and behavior definitions into a standalone shader. Select a complete, fixed-duration episode with a deterministic hash of the episode slot and a build-time seed. Each episode begins and ends at the home anchor. Evaluate clip frame, horizontal position, and orientation directly from time. Quiet, Active, and Sleeping use cursor-change age and focus; prototype thresholds are 10 and 120 seconds. A 0.65-second fade/recenter masks a trajectory reset after a cursor change, at the Active→Sleeping threshold, and after refocus. No frame history, `iFrame`, or runtime service is used.

**Consequences:** Identical surfaces may choose identical episodes. Cursor changes are an imperfect activity proxy, and an unfocused surface may not redraw. An immediate unfocus can change the logical pose without a transition because the shader does not receive focus-loss time. The brief fade conceals a mode reset on rendered frames but does not preserve the former trajectory mathematically. Source metadata, not generic engine code, defines episode clips, durations, weights, positions, and palette.

**Tradeoff:** Fixed slots leave an idle tail when an episode is shorter than its slot. This is intentional rest time and guarantees a continuous home pose at slot boundaries. Long sessions may eventually expose float32 `iTime` precision limits; M3 tests representative time jumps and documents this limit.
