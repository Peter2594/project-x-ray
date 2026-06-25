# Project X-Ray — Example: FastAPI Service

> Sample output for a Python FastAPI backend (SQLAlchemy, PostgreSQL, Redis, Celery). Illustrative.

## 1. Executive Summary

| Field | Value |
|---|---|
| Project Name | `orders-api` |
| Project Purpose | Order management and payment orchestration backend |
| Primary Users | Internal services + storefront frontend (REST) |
| Technology Stack | Python 3.11, FastAPI, SQLAlchemy, PostgreSQL, Redis, Celery |
| Estimated Complexity | High |
| Architecture Style | Layered (router → service → repository), **confidence 88%** |

## 2. System Overview

- **Main responsibilities:** order lifecycle, payment processing, inventory reservation, notifications.
- **Core features:** create/track orders, charge via Stripe, async fulfillment via Celery.
- **Major subsystems:** HTTP API (`app/api/`), domain services (`app/services/`), persistence (`app/repositories/`, `app/models/`), background workers (`app/workers/`).

## 3. Technology Stack

- **Languages:** Python 3.11 (`pyproject.toml`).
- **Frameworks:** FastAPI, SQLAlchemy 2.x, Pydantic, Celery — from `pyproject.toml`.
- **Infrastructure:** PostgreSQL, Redis (broker + cache), Docker Compose, Alembic migrations.
- **External Services:** Stripe (`stripe`), SendGrid (`sendgrid`), AWS S3 (`boto3`).

## 4. Architecture Discovery

```
Detected Pattern: Layered / N-tier
Confidence:       88%
```

**Reasoning:** clean `api → services → repositories → models` separation; dependencies flow downward; Pydantic schemas isolate transport from domain. **Deviation:** `app/api/orders.py` calls a repository directly in one endpoint, bypassing the service layer (layer violation).

## 5. Entry Point Analysis

**Entry file:** `app/main.py` (worker entry: `app/workers/celery_app.py`)

```
main.py
 ↓ load Settings (pydantic-settings)
 ↓ create_engine() / sessionmaker
 ↓ FastAPI(lifespan=...)  → init Redis pool
 ↓ include_router() × N    (app/api/*)
 ↓ uvicorn serves ASGI app
```

## 6. Dependency Analysis

**Most-referenced modules**

| Module | Referenced by | Why it matters |
|---|---|---|
| `app/db/session.py` | 27 modules | DB session dependency everywhere |
| `app/services/auth.py` | 19 modules | request authn/authz |

**High-coupling areas**

| Module | Fan-in | Fan-out | Coupling | Risk |
|---|---|---|---|---|
| `app/services/payment.py` | high | high | High | touches orders, inventory, Stripe, notifications |

**Circular dependencies:** `app/services/order.py ↔ app/services/payment.py` (mutual import) — **flagged**.

## 7. Business Capability Mapping

| Capability | Core? | Where it lives |
|---|---|---|
| Order Processing | ★ Core | `app/services/order.py` |
| Payment | ★ Core | `app/services/payment.py` |
| Inventory reservation | | `app/services/inventory.py` |
| Authentication | | `app/services/auth.py` |
| Notifications | | `app/workers/notify.py` |

## 8. Critical User Flows

**Create order + charge**

```
POST /orders                 (app/api/orders.py:30)
 ↓ OrderService.create()     (app/services/order.py:44)
 ↓ InventoryService.reserve()(app/services/inventory.py:22)
 ↓ PaymentService.charge()   (app/services/payment.py:61)  → Stripe
 ↓ OrderRepository.save()    (app/repositories/order.py:18) → PostgreSQL
 ↓ enqueue notify task       (app/workers/notify.py)        → Redis/Celery
```

## 9. Critical Files

| Rank | File | Responsibility | Dependents | Change impact | Risk |
|---|---|---|---|---|---|
| 1 | `app/services/payment.py` | charge/refund orchestration | 14 | all money movement | **Critical** |
| 2 | `app/db/session.py` | DB session provider | 27 | all persistence | High |
| 3 | `app/services/order.py` | order lifecycle | 16 | core domain | High |

## 10. Technical Debt Assessment

| Category | Smell | Location | Severity |
|---|---|---|---|
| Architecture | Circular dependency | `order ↔ payment` | High |
| Architecture | Layer violation | `api/orders.py` → repository | Medium |
| Code | God object | `services/payment.py` (520 lines, 11 methods) | High |
| Operational | Broad `except Exception` swallowing errors | `workers/notify.py:40` | Medium |

## 11. Blast Radius Analysis

```
File:                app/services/payment.py
Potentially affected: Order creation, Refunds, Inventory release, Notifications
Blast Radius:         High
```

## 12. Bus Factor Estimation

```
Bus Factor: 1–2
Risk:       High
Reason:     payment.py — 520 lines, thin docstrings, 14 dependents,
            ~80% authored by a single contributor (git shortlog).
```

## 13. Learning Roadmap

- **First hour:** `README.md`, `app/main.py`, `app/core/config.py`.
- **First day:** `app/api/` routers, `app/services/order.py`, `app/db/`.
- **First week:** payment + inventory services, Celery workers, Alembic migrations.

## 14. Questions Worth Asking

- Why do `order` and `payment` services import each other — can the cycle be broken with an interface/event?
- Is the direct repository call in `api/orders.py` intentional (perf) or an oversight?
- What's the retry/idempotency story for Stripe charges?

## 15. Final Verdict

| Metric | Value |
|---|---|
| Repository Health Score | 68 / 100 |
| Maintainability | Fair |
| Onboarding Difficulty | Medium–Hard |
| Refactoring Risk | High |

Sub-scores: structure 14/20, tests 14/20, docs 9/15, coupling 9/15, debt 10/15, bus factor 12/15.
