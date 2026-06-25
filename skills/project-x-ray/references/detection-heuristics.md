# Detection Heuristics

Rules for classifying what you find and for scoring the report. These are heuristics, not laws — always pair a classification with a confidence level and the evidence behind it.

---

## Architecture Pattern Detection

Score each pattern by how many of its signals are present, then report the dominant one with a confidence %.

| Pattern | Strong signals |
|---|---|
| **Layered / N-tier** | Folders split into `controllers` → `services` → `repositories` → `models`; dependencies flow one direction (down). |
| **Clean / Hexagonal** | A `domain`/`core` package with no framework imports; `ports`/`adapters` or `interfaces`/`infrastructure` folders; dependency inversion (inner layers define interfaces, outer implement). |
| **MVC** | `models`, `views`, `controllers` (or `templates`); framework like Rails/Django/Spring MVC/Laravel. |
| **Modular Monolith** | One deployable, but clear internal module boundaries (`modules/billing`, `modules/orders`) with limited cross-module imports. |
| **Microservices** | Multiple deployables/services, each with its own manifest + Dockerfile; inter-service calls over HTTP/gRPC/queue; per-service datastores. |
| **Event-driven** | Message broker (Kafka/RabbitMQ/SNS), publishers/subscribers, handlers keyed by event type. |
| **Pipeline / Batch** | Stages reading and writing through queues or files; job schedulers (Airflow, cron). |

**Confidence rubric:** count matched signals vs. expected. 4–5/5 → 85–95%. 2–3/5 → 60–80%. ≤1 → say "unclear / hybrid" and list the competing candidates. Always note deviations (e.g. "Layered, but services reach into controllers in 3 places — layer violation").

---

## Criticality Ranking

Rank files by **impact**, not size. Composite signal:

```
criticality ≈ (fan-in references) + (capabilities it participates in) + (change frequency / churn)
```

A file is **critical** when it scores high on multiple axes. Record for each: Responsibility (one line), Dependency count (fan-in), Change impact (which flows break if it's wrong), Risk level.

---

## Coupling Thresholds

Rough guidance for a medium repo (calibrate to project size):

| Metric | Low | Medium | High |
|---|---|---|---|
| Fan-in (modules importing this) | <5 | 5–15 | >15 |
| Fan-out (modules this imports) | <8 | 8–20 | >20 |
| Both high simultaneously | — | — | **Coupling hotspot — flag it** |

Circular dependency between two modules = always flag, regardless of counts.

---

## Technical Debt Smells

| Category | Smell | How to spot |
|---|---|---|
| **Code** | God object | One file/class with very high LOC + many responsibilities + high fan-in |
| | Long function | Functions >75 lines or deeply nested |
| | Duplicate logic | Same validation/transform repeated across modules |
| | Dead code | Symbols defined but never referenced; unreachable branches |
| **Architecture** | Circular dependency | Mutual imports between modules |
| | Layer violation | Lower layer importing an upper layer (repo importing controller) |
| | Tight coupling | Coupling hotspots from the table above |
| **Operational** | Missing logging | Critical paths (auth, payments) with no log/trace calls |
| | Missing tests | Core modules with no corresponding test file |
| | Weak error handling | Empty `catch`/`except`, swallowed errors, broad bare excepts |

**Severity:** weight by (likelihood of being hit) × (blast radius). Auth/payments/data-loss paths default to **Critical** or **High**.

---

## Bus Factor

| Bus factor | Meaning | Typical evidence |
|---|---|---|
| 1 | One person holds the knowledge | Single author on a large, undocumented, heavily-depended-on file |
| 2–3 | Thin coverage | A few authors, sparse docs |
| 4+ | Healthy | Many contributors, tests + docs present |

No git history available → **Unknown** (state why).

---

## Repository Health Score (0–100)

A transparent, weighted rubric. Show the sub-scores, not just the total.

| Dimension | Weight | Full marks when… |
|---|---|---|
| Structure & modularity | 20 | Clear layers/modules, low circular deps |
| Test coverage breadth | 20 | Core capabilities have tests |
| Documentation | 15 | README + per-module docs + setup instructions |
| Coupling health | 15 | Few/no coupling hotspots |
| Debt load | 15 | Few critical/high smells |
| Bus-factor resilience | 15 | Knowledge spread across contributors |

Map the total to a verdict:

| Score | Maintainability | Onboarding difficulty | Refactoring risk |
|---|---|---|---|
| 85–100 | Excellent | Easy | Low |
| 70–84 | Good | Medium | Medium |
| 50–69 | Fair | Medium–Hard | High |
| <50 | Poor | Hard | Very High |

The three verdict columns are independent reads — a codebase can be maintainable yet hard to onboard, or easy to read yet risky to change.
