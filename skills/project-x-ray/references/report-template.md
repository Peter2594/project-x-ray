# Project X-Ray Report Template

Fill every section from evidence gathered in the investigation playbook. Delete sections that genuinely don't apply to a tiny repo, but never fabricate detail to fill one. Mark anything unverified as **Unknown** or attach a confidence level.

---

## 1. Executive Summary

| Field | Value |
|---|---|
| Project Name | |
| Project Purpose | |
| Primary Users | |
| Technology Stack | |
| Estimated Complexity | Low / Medium / High |
| Architecture Style | _(pattern + confidence %)_ |

## 2. System Overview

- **Main responsibilities:** …
- **Core features:** …
- **Major subsystems:** …

> Example: "This application manages inventory, order fulfillment, and payment processing for e-commerce operations."

## 3. Technology Stack

- **Languages:** …
- **Frameworks:** …
- **Infrastructure:** …
- **External Services:** …

_(Each entry cites the manifest/import that proves it.)_

## 4. Architecture Discovery

```
Detected Pattern: <pattern>
Confidence:       <NN>%
```

**Reasoning:** which signals matched (folder layout, dependency direction, deployables). **Deviations:** layer violations or hybrid traits observed.

## 5. Entry Point Analysis

**Entry file(s):** `path` …

**Startup sequence:**

```
main
 ↓ load_config()
 ↓ initialize_database()
 ↓ register_routes()
 ↓ start_server()
```

## 6. Dependency Analysis

**Most-referenced modules**

| Module | Referenced by | Why it matters |
|---|---|---|
| `auth_service.py` | 23 modules | central auth |

**High-coupling areas**

| Module | Fan-in | Fan-out | Coupling | Risk |
|---|---|---|---|---|
| `payment_service.py` | high | high | High | … |

**Circular dependencies:** … (or none found)

## 7. Business Capability Mapping

| Capability | Core? | Where it lives |
|---|---|---|
| Authentication | | `…` |
| User Management | | `…` |
| Order Processing | ★ Core | `…` |
| Billing | | `…` |
| Reporting | | `…` |

## 8. Critical User Flows

Trace 2–3 flows with real file paths.

**Example — User Login**

```
Browser
 ↓ POST /login        (routes/auth.py:12)
 ↓ AuthController     (controllers/auth.py:34)
 ↓ AuthService        (services/auth_service.py:50)
 ↓ UserRepository     (repositories/user.py:20)
 ↓ Database
```

## 9. Critical Files

| Rank | File | Responsibility | Dependents | Change impact | Risk |
|---|---|---|---|---|---|
| 1 | `auth_service.py` | central authentication logic | 23 | login/registration/reset | High |

## 10. Technical Debt Assessment

| Category | Smell | Location | Severity |
|---|---|---|---|
| Code | God object | `payment_processor.py` | High |
| Architecture | Circular dependency | `a ↔ b` | Medium |
| Operational | Missing tests | `services/billing.py` | High |

Severity scale: Critical / High / Medium / Low.

## 11. Blast Radius Analysis

```
File:                auth_service.py
Potentially affected: Login, Registration, Password Reset, Admin Auth
Blast Radius:         High
```

Repeat for each critical file.

## 12. Bus Factor Estimation

```
Bus Factor: 1–2
Risk:       High
Reason:     payment_processor.py — 3,400 lines, no docs, 17 dependents,
            single author (git log)
```

## 13. Learning Roadmap

- **First hour:** `README.md`, entry point, config.
- **First day:** routes → controllers → services.
- **First week:** core business logic, database layer, external integrations.

## 14. Questions Worth Asking

Questions a new engineer should raise with the team — surface real ambiguities you found:

- Why are there two payment services?
- Why is Redis required for authentication?
- Why is order validation duplicated across modules?

## 15. Final Verdict

| Metric | Value |
|---|---|
| Repository Health Score | NN / 100 |
| Maintainability | Excellent / Good / Fair / Poor |
| Onboarding Difficulty | Easy / Medium / Hard |
| Refactoring Risk | Low / Medium / High |

Include the sub-scores behind the health number (see detection-heuristics.md).

---

> **Guiding principle:** Don't explain files. Explain the system. Build the mental model first, then dive into implementation details.
