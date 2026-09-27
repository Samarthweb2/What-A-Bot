# Pitch & Demo Framing

## 1. Three-Minute Demo (Section M)

| Time | Action |
|---|---|
| 0:00–0:25 | State the narrow problem hypothesis; name the evidence as proxy, not merchant. |
| 0:25–0:45 | Show catalog + a recorded offline stock change. |
| 0:45–1:40 | Send the Hinglish budget/quantity request; show real candidate retrieval + selected basket. |
| 1:40–2:10 | Confirm the quote; show invoice + stock update. |
| 2:10–2:40 | Show proxy results, measured latency/cost, one verified replay result. |
| 2:40–3:00 | State deployment/evidence limits; name the next step as a merchant pilot. |

*(Note: If latency overruns, drop the contrasting case, not the core flow. No live restart. Any fallback recording must be explicitly labelled as recorded.)*

---

## 2. Pitch Framing (Section N)

> "We're testing whether a small stationery shop can handle budget-constrained WhatsApp orders without manually searching every combination. The customer can mix Hindi and English, specify a budget and product requirements, and approve a basket drawn from current stock. The agent selects the basket; the backend checks every requirement and records the order safely. We tested the workflow with [N] proxies — not merchants — and observed [results]. Stock updates are manual today, and the next step is a merchant pilot."

*(Note: Don't claim tool-use itself is novel — Meta already markets business agents that take actions. The differentiation is this specific demonstrated workflow and its evidence, not "other bots are decision trees.")*

---

## 3. Scaling Claim (Section O)

> "Data and authorization are tenant-scoped. This prototype intentionally runs one process; production throughput and merchant onboarding are not established."

*(Note: Next scaling work: durable worker coordination, sender onboarding, real inventory integration, measured cost at volume. A pooled DB connection and two seeded businesses are not proof of national scale — don't oversell them as such.)*

---

## 4. Evidence to Show (Section L)
- **Normalized constraints**
- **Actual candidate rows** returned by `find_options`
- **Model-selected quantities**
- **Validation result**
- **Quote/order ID + status**
- **Stock before/after**
- **Outbox state**
- **Observed latency/cost**: [Placeholder ms] / [Placeholder ₹]
- **Proxy results with stated limitations**: [Placeholder Manual vs Agent data]
