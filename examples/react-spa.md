# Project X-Ray — Example: React SPA

> Sample output for a typical React + TypeScript single-page application (Vite, Redux Toolkit, React Query). Illustrative — file paths and numbers are representative of a real codebase of this shape.

## 1. Executive Summary

| Field | Value |
|---|---|
| Project Name | `storefront-web` |
| Project Purpose | Customer-facing storefront UI for an e-commerce platform |
| Primary Users | End shoppers (browser) |
| Technology Stack | TypeScript, React 18, Vite, Redux Toolkit, React Query, Tailwind |
| Estimated Complexity | Medium |
| Architecture Style | Feature-sliced SPA (component → hook → API client), **confidence 82%** |

## 2. System Overview

- **Main responsibilities:** product browsing, cart, checkout, account management.
- **Core features:** catalog search, cart/checkout flow, auth, order history.
- **Major subsystems:** routing shell, feature modules (`catalog`, `cart`, `checkout`, `account`), shared API layer, design-system components.

## 3. Technology Stack

- **Languages:** TypeScript (`tsconfig.json`), CSS.
- **Frameworks:** React 18, React Router 6, Redux Toolkit, TanStack Query — from `package.json`.
- **Infrastructure:** Vite build, deployed as static assets (`Dockerfile` → nginx).
- **External Services:** REST API gateway (`VITE_API_URL`), Stripe.js (`@stripe/stripe-js`), Sentry.

## 4. Architecture Discovery

```
Detected Pattern: Feature-sliced SPA
Confidence:       82%
```

**Reasoning:** `src/features/<domain>/` folders each bundle components, hooks, and a slice; shared concerns in `src/shared/`. Data fetching isolated behind `src/shared/api/` clients consumed via React Query hooks. **Deviation:** two features import each other's components directly (`checkout` → `cart`) instead of via `shared` — minor coupling.

## 5. Entry Point Analysis

**Entry file:** `src/main.tsx`

```
main.tsx
 ↓ create root
 ↓ <QueryClientProvider>
 ↓ <Provider store={store}>      (Redux)
 ↓ <BrowserRouter>
 ↓ <App />                       (route table in src/app/routes.tsx)
```

## 6. Dependency Analysis

**Most-referenced modules**

| Module | Referenced by | Why it matters |
|---|---|---|
| `src/shared/api/client.ts` | 31 modules | every network call routes through it |
| `src/shared/auth/useAuth.ts` | 18 modules | gates protected routes & requests |

**High-coupling areas**

| Module | Fan-in | Fan-out | Coupling | Risk |
|---|---|---|---|---|
| `src/app/store.ts` | high | high | High | wires every feature slice |

**Circular dependencies:** none detected.

## 7. Business Capability Mapping

| Capability | Core? | Where it lives |
|---|---|---|
| Catalog browsing | ★ Core | `src/features/catalog/` |
| Cart | ★ Core | `src/features/cart/` |
| Checkout / Payment | ★ Core | `src/features/checkout/` |
| Authentication | | `src/shared/auth/` |
| Account / Orders | | `src/features/account/` |

## 8. Critical User Flows

**Checkout**

```
<CheckoutPage>            (features/checkout/CheckoutPage.tsx:24)
 ↓ useCheckout()          (features/checkout/useCheckout.ts:18)
 ↓ api.orders.create()    (shared/api/orders.ts:40)
 ↓ Stripe.confirmPayment  (features/checkout/payment.ts:55)
 ↓ POST /orders → API gateway
```

## 9. Critical Files

| Rank | File | Responsibility | Dependents | Change impact | Risk |
|---|---|---|---|---|---|
| 1 | `shared/api/client.ts` | axios instance, auth header, error normalization | 31 | all data flows | High |
| 2 | `shared/auth/useAuth.ts` | session/token state | 18 | login, guarded routes | High |
| 3 | `app/store.ts` | Redux store composition | high | global state | Medium |

## 10. Technical Debt Assessment

| Category | Smell | Location | Severity |
|---|---|---|---|
| Code | Long component | `features/checkout/CheckoutPage.tsx` (310 lines) | Medium |
| Architecture | Feature-to-feature import | `checkout → cart` | Low |
| Operational | Sparse tests | `features/checkout/` has no unit tests | High |

## 11. Blast Radius Analysis

```
File:                shared/api/client.ts
Potentially affected: every feature that fetches data (all of them)
Blast Radius:         High
```

## 12. Bus Factor Estimation

```
Bus Factor: 2–3
Risk:       Medium
Reason:     checkout feature authored mostly by one contributor (git log),
            but shared/ is broadly owned.
```

## 13. Learning Roadmap

- **First hour:** `README.md`, `src/main.tsx`, `src/app/routes.tsx`.
- **First day:** `shared/api/`, `shared/auth/`, one full feature (`catalog`).
- **First week:** `checkout` flow end to end, Redux store wiring, Stripe integration.

## 14. Questions Worth Asking

- Why does `checkout` import from `cart` directly instead of `shared`?
- Is there a reason checkout has no tests — is it covered by E2E elsewhere?
- Are we standardizing on React Query or Redux for server state? Both are present.

## 15. Final Verdict

| Metric | Value |
|---|---|
| Repository Health Score | 76 / 100 |
| Maintainability | Good |
| Onboarding Difficulty | Medium |
| Refactoring Risk | Medium |

Sub-scores: structure 16/20, tests 11/20, docs 12/15, coupling 12/15, debt 11/15, bus factor 14/15.
