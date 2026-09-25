# BACKROW 11.0 — Controlled Closure Matrix

This is a **controllable-product closure** score, not a prediction that judges must award first place.

| Gate | Status | Evidence |
|---|---|---|
| Core web product runs | PASS | browser/API tests |
| Whole-deck automatic matching | PASS | 3/3 bundled deck, no page index |
| Exact critical-value guard | PASS | `2.5% → 25%` |
| Custom AudienceNet runtime | PASS | AudienceNet 2.0 loaded and used |
| Custom-model procedural baseline gain | PASS | macro-F1 0.9422 vs 0.4789 strongest simple baseline |
| Learned channel non-cosmetic | PASS | ablation escalation verified |
| Hard-evidence safety hierarchy | PASS | direct evidence overrides pessimistic learned output |
| Fix → rescan loop | PASS | 2 risk → 0 risk in controlled regression |
| Fail-closed behavior | PASS | wrong/ambiguous input rejection |
| Security/privacy study separation | PASS | token + truth separation + immutable responses |
| Physical validation collector | PASS | timing/deck console + locked evaluator |
| English product | PASS | desktop/mobile browser tests |
| Indonesian product | PASS | main + validation + reader + admin browser tests |
| English competition deck | PASS | slide overflow test |
| Indonesian competition deck | PASS | slide overflow test + rendered montage |
| Release hygiene | PASS | clean packaging + manifest verification |

**Controllable closure: 16 / 16 = 100%.**

## External empirical gates still required for a human-readability claim

- real projector/display conditions;
- naïve human readers;
- multiple rooms and audience positions;
- manual-vs-BACKROW measurement;
- locked frontier multimodal baseline on the same physical evidence.

Those gates cannot be replaced by generated data. The supplied field-study stack is designed to collect them without changing the evaluation after results are seen.
