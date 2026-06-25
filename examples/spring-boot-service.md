# Project X-Ray — Example: Spring Boot Service

> Sample output for a Java Spring Boot service (Spring Web, Spring Data JPA, PostgreSQL, Kafka). Illustrative.

## 1. Executive Summary

| Field | Value |
|---|---|
| Project Name | `inventory-service` |
| Project Purpose | Inventory and stock-reservation microservice |
| Primary Users | Other backend services (REST + Kafka events) |
| Technology Stack | Java 17, Spring Boot 3, Spring Data JPA, PostgreSQL, Kafka |
| Estimated Complexity | Medium–High |
| Architecture Style | Layered MVC + event-driven, **confidence 85%** |

## 2. System Overview

- **Main responsibilities:** track stock levels, reserve/release inventory, publish stock events.
- **Core features:** stock CRUD, reservation with optimistic locking, Kafka event publication/consumption.
- **Major subsystems:** REST controllers, service layer, JPA repositories, Kafka listeners/producers.

## 3. Technology Stack

- **Languages:** Java 17 (`pom.xml`).
- **Frameworks:** Spring Boot 3, Spring Web, Spring Data JPA, Spring Kafka — from `pom.xml`.
- **Infrastructure:** PostgreSQL, Apache Kafka, Docker, Flyway migrations.
- **External Services:** schema registry; downstream `orders-service` via events.

## 4. Architecture Discovery

```
Detected Pattern: Layered MVC + event-driven
Confidence:       85%
```

**Reasoning:** classic `controller → service → repository` packages with Spring stereotypes (`@RestController`, `@Service`, `@Repository`); plus `@KafkaListener` consumers and a producer component for async integration. **Deviation:** one controller injects a repository directly (`@Autowired StockRepository`) — layer violation.

## 5. Entry Point Analysis

**Entry file:** `src/main/java/com/acme/inventory/InventoryApplication.java`

```
InventoryApplication.main()
 ↓ SpringApplication.run()
 ↓ component scan + auto-config
 ↓ DataSource + JPA EntityManager
 ↓ Kafka consumer/producer factories
 ↓ Embedded Tomcat serves REST
```

## 6. Dependency Analysis

**Most-referenced modules**

| Module | Referenced by | Why it matters |
|---|---|---|
| `service/StockService.java` | 12 classes | central domain logic |
| `repository/StockRepository.java` | 9 classes | persistence access |

**High-coupling areas**

| Module | Fan-in | Fan-out | Coupling | Risk |
|---|---|---|---|---|
| `service/ReservationService.java` | high | high | High | coordinates stock, locking, events |

**Circular dependencies:** none detected (Spring would fail to start on constructor cycles).

## 7. Business Capability Mapping

| Capability | Core? | Where it lives |
|---|---|---|
| Stock management | ★ Core | `service/StockService.java` |
| Reservation | ★ Core | `service/ReservationService.java` |
| Event publication | | `messaging/StockEventProducer.java` |
| Event consumption | | `messaging/OrderEventListener.java` |

## 8. Critical User Flows

**Reserve stock**

```
POST /reservations              (web/ReservationController.java:28)
 ↓ ReservationService.reserve() (service/ReservationService.java:41)
 ↓ StockRepository (optimistic lock) (repository/StockRepository.java)
 ↓ StockEventProducer.publish()  (messaging/StockEventProducer.java:33) → Kafka
```

**Consume order-placed event**

```
Kafka "orders.placed"
 ↓ OrderEventListener.onOrderPlaced() (messaging/OrderEventListener.java:25)
 ↓ ReservationService.reserve()
```

## 9. Critical Files

| Rank | File | Responsibility | Dependents | Change impact | Risk |
|---|---|---|---|---|---|
| 1 | `service/ReservationService.java` | reservation + concurrency | 8 | core flow + events | High |
| 2 | `service/StockService.java` | stock domain logic | 12 | all stock ops | High |
| 3 | `messaging/StockEventProducer.java` | event contract | 6 | downstream services | Medium |

## 10. Technical Debt Assessment

| Category | Smell | Location | Severity |
|---|---|---|---|
| Architecture | Layer violation | `web/ReportController.java` injects repository | Medium |
| Code | Long method | `ReservationService.reserve()` (90 lines) | Medium |
| Operational | Missing retry/DLQ on consumer | `messaging/OrderEventListener.java` | High |
| Operational | Sparse logging on reservation failures | `ReservationService.java` | Medium |

## 11. Blast Radius Analysis

```
File:                service/ReservationService.java
Potentially affected: Reservation REST, order-event consumer, stock events
Blast Radius:         High
```

## 12. Bus Factor Estimation

```
Bus Factor: 2–3
Risk:       Medium
Reason:     Reservation logic concentrated in one author, but service is
            well-tested (good JUnit coverage) which lowers risk.
```

## 13. Learning Roadmap

- **First hour:** `README.md`, `InventoryApplication.java`, `application.yml`.
- **First day:** controllers, `StockService`, `ReservationService`, JPA entities.
- **First week:** Kafka producer/consumer contracts, optimistic locking, Flyway migrations.

## 14. Questions Worth Asking

- Is there a dead-letter queue / retry policy for failed `orders.placed` consumption?
- Why does `ReportController` bypass the service layer?
- How is the stock-event schema versioned for downstream consumers?

## 15. Final Verdict

| Metric | Value |
|---|---|
| Repository Health Score | 74 / 100 |
| Maintainability | Good |
| Onboarding Difficulty | Medium |
| Refactoring Risk | Medium |

Sub-scores: structure 16/20, tests 15/20, docs 10/15, coupling 11/15, debt 10/15, bus factor 12/15.
