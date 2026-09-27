# EmberGround AI Hackathon — Final Build Plan
## WhatsApp Stationery Order Agent

**Status: locked for build day.** This plan went through five architecture review rounds with ChatGPT Astra (63 → 73 → 76 → 79 → 82/100, plan-projected) plus one final scope correction (n8n restored for notification only). No further planning rounds — remaining risk is resolved by building and testing, not more design.

## Event Context
- EmberGround AI Hackathon 2026 — Sunday, Sept 27, 2026, 9:00 AM – 8:00 PM IST
- Startup Park Bengaluru · Solo build · Track 3 — Bharat Business
- Judging: Problem & Impact 20% · Agentic Depth 25% · Technical Execution 20% · India Impact & Scalability 20% · Wow Factor 15%
- Sponsors: ElevenLabs, n8n, Render

---

## A. Product and Scope

An assistant for a small stationery shop that turns a customer's budget, quantity, and product requirements into an available basket, obtains explicit confirmation, and records the order correctly.

**Problem hypothesis being tested (not claimed as proven):**
> Budget-constrained orders require repeated back-and-forth messages when a requested brand is unavailable or stock is split across alternatives.

**In scope:**
- One product family: notebooks, sold individually
- English and a tested subset of Hinglish (code-switched Hindi-English)
- Quantity, total budget, ruling, size, mixed-brand permission as constraints
- Real catalog lookup, model-selected combinations, validated quotes, order confirmation
- Manual owner-side stock updates (no live POS sync claimed)
- Owner review queue for policy-held (high-value) orders, with an **n8n notification hook** alerting the owner that a hold needs review — approval/rejection itself happens on a protected owner page, not through n8n
- Replay-safe database outcomes; persistent outbound replies via outbox
- A second seeded business, used only for tenant-isolation testing — not demoed live

**Explicitly cut:**
- n8n-driven approval/callback logic (kept only as one-way notification — see below)
- Appointment booking
- Generic merchant onboarding / arbitrary CSV import
- Voice messages, payment processing
- Live process-killing as a demo centerpiece
- Any claim of validated fraud detection — framed as "order-risk review" policy only

The invoice is a demo order invoice, marked unpaid. No payment-verification or tax-compliance claims.

---

## B. Evidence Plan (what actually moves Problem & Impact / India Impact scores)

**Proxy study (30 min, 3 participants):** friends/classmates, explicitly labelled as proxies, not merchants.
- Each does one task manually (catalog sheet) and one matched task via the agent, order alternated, quantities varied to reduce recall bias.
- Record per participant: completion time, validity (quantity/budget/ruling/size/stock all satisfied), corrections needed, abandonment, one usability note.
- Report individual results plainly — no statistical-significance claims from n=3.
- If volunteers aren't available: run and label as developer self-testing, and drop the associated score claim rather than fake it.

**India-specific behaviors (concrete, tested, not just claimed):**
1. Tested code-switched input, e.g. *"12 A5 ruled copies chahiye, total 600 ke andar. Mixed brands chalega, plain mat dena."* — note size (A5) is included explicitly, since `find_options` requires it; if a real message omits size, the agent must clarify, not silently assume A5. Normalized into structured constraints, shown back in the quote for confirmation. Test negation, numbers, budget interpretation explicitly — don't claim broad multilingual support.
2. Manual offline-stock-update path on the owner page (record a sale / correct a count, shows last-updated time), proving a workable (if manual) maintenance path.
3. Visible operating cost: track model + Twilio + Meta charges against completed orders, including failed attempts in the numerator. Use event-day rate cards, state currency, no invented exchange rates.

---

## C. Architecture

```
WhatsApp
  → signature-validated Twilio webhook
  → persist inbound event + bound tenant
  → acknowledge with empty TwiML

Single application process (one worker)
  → ordered inbox dispatcher (shared lock registry for live + recovery)
  → model reads catalog, selects action
  → one successful terminal action commits, in ONE transaction:
       business result + message_outcomes row + outbox row + inbox completed
  → independent outbox sender → Twilio → delivery-status callbacks

Held order (policy threshold crossed)
  → draft → held (no stock deducted, no invoice)
  → fire-and-forget n8n workflow: notifies owner a hold needs review
    (n8n never touches order state — pure notification, no callback auth needed)
  → owner approves/rejects on the protected owner page (same DB, same CAS pattern)

Protected owner page
  → stock adjustments, held-order approve/reject, trace/failed-work/uncertain-sends view
```

Deployment: one Render instance, one worker process, no deploys during judging, Neon pooled connection for short transactions, no DB transaction held open during inference or approval, one sender loop. External DB-touching health check every 3 minutes to mitigate idle sleep (Render can still restart — this is mitigation, not a guarantee).

---

## D. Schema

Money in integer paise. Quantities positive integers. Stock never negative. **Note: this is a schema specification, not executable SQL** — when translating to an actual migration, add the required `NOT NULL` constraints and valid `CHECK (...)` expressions explicitly; don't paste it in as-is.

```sql
businesses
  business_id TEXT PRIMARY KEY
  name TEXT
  review_above_paise INTEGER
  faq JSONB

catalog
  business_id TEXT REFERENCES businesses
  sku TEXT
  name TEXT
  brand TEXT
  ruling TEXT CHECK IN ('ruled', 'unruled')
  size TEXT CHECK IN ('A4', 'A5')
  unit_price_paise INTEGER CHECK > 0
  qty INTEGER CHECK >= 0
  updated_at TIMESTAMPTZ
  PRIMARY KEY (business_id, sku)

sessions
  session_id UUID PRIMARY KEY
  customer_phone TEXT
  destination TEXT
  active_business_id TEXT REFERENCES businesses
  UNIQUE (customer_phone, destination)

inbox
  input_id TEXT PRIMARY KEY            -- 'wa:<MessageSid>' or 'owner:<nonce>', never model-supplied
  sequence BIGSERIAL UNIQUE
  source TEXT CHECK IN ('whatsapp', 'owner')
  session_id UUID REFERENCES sessions
  business_id TEXT REFERENCES businesses
  body JSONB
  status TEXT CHECK IN ('received', 'processing', 'completed', 'attention')
  attempts INTEGER DEFAULT 0
  next_attempt_at TIMESTAMPTZ
  last_error TEXT
  created_at TIMESTAMPTZ

orders
  order_id UUID PRIMARY KEY
  quote_code TEXT UNIQUE
  origin_input_id TEXT UNIQUE REFERENCES inbox
  session_id UUID REFERENCES sessions
  business_id TEXT REFERENCES businesses
  status TEXT CHECK IN ('draft', 'held', 'confirmed', 'cancelled')
  constraints JSONB
  items JSONB                          -- immutable after creation
  total_paise INTEGER CHECK >= 0
  expires_at TIMESTAMPTZ
  created_at TIMESTAMPTZ
  UNIQUE (business_id, order_id)

invoices
  order_id UUID PRIMARY KEY REFERENCES orders
  invoice_id UUID UNIQUE
  payload JSONB
  created_at TIMESTAMPTZ

message_outcomes
  input_id TEXT PRIMARY KEY REFERENCES inbox
  order_id UUID NULL REFERENCES orders
  kind TEXT
  result JSONB
  created_at TIMESTAMPTZ

outbox
  outbox_id UUID PRIMARY KEY
  event_key TEXT UNIQUE
  input_id TEXT REFERENCES message_outcomes
  session_id UUID REFERENCES sessions
  business_id TEXT REFERENCES businesses
  payload JSONB
  state TEXT CHECK IN ('pending', 'sending', 'accepted', 'unknown', 'failed')
  attempt_no INTEGER DEFAULT 0
  twilio_sid TEXT NULL
  delivery_status TEXT NULL
  next_attempt_at TIMESTAMPTZ
  created_at TIMESTAMPTZ

events                                 -- tool traces, costs, owner changes, provider-status observations
  event_id BIGSERIAL PRIMARY KEY
  input_id TEXT
  kind TEXT
  data JSONB
  created_at TIMESTAMPTZ
```

**Order state machine (DB-enforced, one-way):**
```
draft → confirmed | held | cancelled
held  → confirmed | cancelled
confirmed → (no further transition)
cancelled → (no further transition)
```
A trigger rejects any other transition or edit to immutable order fields. **Corrections create a new quote**, atomically cancelling the previous open quote for that customer/business — confirmed orders are never affected.

---

## E. Tool Contracts

Backend context (`input_id`, `session_id`, `business_id`, `customer_phone`, `authorized_quote_id`) is injected — never a model-editable argument.

```python
find_options(
    quantity: int, budget_paise: int,
    ruling: Literal["ruled", "unruled"], size: Literal["A4", "A5"],
    allow_mixed_brands: bool
) -> CandidateSet
# Returns INDIVIDUAL eligible candidates only — never a precomputed winning basket.
# Never claims infeasibility just because the model hasn't found a solution.

propose_order(
    candidate_set_id: str, items: list[{"sku": str, "qty": int}]
) -> Quote | ValidationError
# find_options stores the normalized constraints behind the opaque candidate_set_id,
# bound to the current input/session/business. propose_order resolves those stored
# constraints server-side (never re-trusts the model's restated constraints) and
# REQUIRES the sum of selected quantities to equal the requested quantity —
# without this check, a perfectly priced 11-notebook basket could pass for a
# 12-notebook request. Also validates budget, size, ruling, brand-mixing
# permission, and current catalog data. Unknown/missing required constraints
# trigger clarification. Computes price/total itself.
# On success: creates the immutable draft AND its outcome/reply, atomically.
# Terminal action — model loop stops after a successful commit.

confirm_order(order_id: str) -> Confirmed | Held | StaleQuote | AlreadyResolved
# Requires an explicit customer command (e.g. "CONFIRM Q7K2").
# Backend resolves the quote and injects authorization — never model-invented.
# Checks session, tenant, expiry, status, stock, current price.
# Returns the existing result if already resolved. Can be routed deterministically —
# no unnecessary model call just to look more agentic.

answer_faq(question: str) -> SupportedAnswer | NeedsOwner

finish_reply(kind: Literal["clarification","faq","needs_owner"], text: str) -> PersistedReply
```

---

## F. Transaction & Replay Rules

Every terminal action uses the same pattern — transaction begins **after** the model has decided; no model/network call runs inside it:

```
BEGIN
  Lock inbox row by input_id.
  If message_outcomes exists: return stored result, do not repeat effects.
  Validate the proposed action.
  Perform the business action, if any.
  INSERT message_outcomes.
  INSERT outbox (unique event_key).
  UPDATE inbox SET status = 'completed'.
COMMIT
```

**The real guarantee: one committed outcome per accepted input — not "the agent only ever runs once."** Inference may legitimately re-run after a crash; it just can never produce a second business effect, because it re-hits the `message_outcomes` check first.

Confirmation CAS:
```sql
UPDATE orders SET status = 'confirmed'
WHERE order_id = :order_id AND business_id = :business_id
  AND session_id = :session_id AND status = :expected_status
RETURNING order_id;
```
`expected_status` is `draft` for ordinary customer confirmation, `held` for owner approval.

Stock decrement, per SKU, in sorted SKU order (reduces deadlock risk; aborted transactions are rolled back and retried within a bounded policy), business-scoped:
```sql
UPDATE catalog SET qty = qty - :quantity, updated_at = now()
WHERE business_id = :business_id AND sku = :sku
  AND qty >= :quantity AND unit_price_paise = :quoted_price
RETURNING qty;
```
One returned row required per item; any failure rolls back the whole confirmation including the status transition. If stock/price changed, return a structured stale-quote result and persist a reply asking the customer to re-quote — never silently substitute.

---

## G. Holds, Owner Actions, n8n Notification

Configurable order-value threshold = a **demonstration review policy**, not a validated fraud predictor.

```
customer confirms above threshold:
  draft → held (no stock deducted, no invoice)
  persist customer reply + owner-visible held order
  [transaction commits]
  AFTER commit: best-effort notification to ONE configured n8n production webhook
```
**Pick one notification destination before the event** (e.g. n8n → owner's WhatsApp) — "WhatsApp/Slack/email" is not a real decision, it's an unresolved integration choice that needs to be closed now, not on the day.

The notification call happens strictly *after* the held-order transaction commits — never inside it. It's authenticated with a shared secret, has a short timeout, and its success/failure is recorded in `events`. **Notification failure never changes the order outcome or blocks the customer reply** — the persisted owner queue remains the authoritative review mechanism regardless of whether the ping arrives. The notification contains an order reference and a link to the protected owner page — never approval credentials, since n8n still never authorizes anything or receives a callback. Removing approval callbacks removed their token-security work; it does **not** remove authentication from the n8n trigger itself or from the owner page.

Owner approve/reject happens on the protected page, using the **same CAS + transaction pattern** as customer confirmation, with `expected_status = 'held'`. Repeat actions return the stored/current terminal state. Because quotes are immutable, approval can never authorize a since-edited basket.

Stock updates are owner-only, validated, audited via `events` — the customer-facing agent has no inventory-editing tool.

---

## H. Dispatcher & Recovery

- In-process lock registry, shared by live intake and recovery, processes each conversation's pending input in order.
- Webhook intake never waits on the model or the conversation lock.
- Startup: requeue interrupted `processing` rows, leave committed outcomes untouched, leave pending outbox entries alone, mark interrupted `sending` rows `unknown`.
- Runtime: catch processing exceptions, bounded retry with backoff, after limit mark `attention` and surface on the owner page — never silently stuck in `processing`.
- Sender: claim one pending outbox row → mark `sending` → call Twilio outside the transaction → record SID/state. Status callbacks are signature-validated and correlated by outbox ID + attempt number (an older attempt's callback can't overwrite a newer one). Ambiguous sends are marked `unknown`, not auto-retried — owner page offers explicit retry with a duplicate-message warning.

---

## I. Fixture Catalog & Flagship Task

| SKU | Ruling | Size | Price | Stock |
|---|---|---|---:|---:|
| A | Ruled | A5 | ₹40 | 5 |
| B | Ruled | A5 | ₹50 | 4 |
| C | Ruled | A5 | ₹60 | 5 |
| D | Unruled | A5 | ₹25 | 30 |

Task: *"12 A5 ruled notebooks, mixed brands allowed, maximum ₹600."* (size included explicitly — the agent must ask for it if a real customer omits it, never assume)

Verified by exhaustive enumeration (test harness only — never the agent's runtime):
| A stock | Expected result |
|---:|---|
| 5 | Four feasible baskets, min cost ₹580 |
| 4 | Exactly one: 4A+4B+4C = ₹600 |
| 3 | Infeasible, min for 12 is ₹620 |

On no valid basket: *"I couldn't construct a valid basket within those limits. Would you prefer fewer notebooks or a higher budget?"* — never claim mathematical impossibility from an unsuccessful search. Hard requirements (e.g. ruled-only) stay fixed until the customer explicitly authorizes a change.

---

## J. Verification Checklist (required before demo)

| Test | Required observation |
|---|---|
| Duplicate inbound input | One outcome, one order action |
| Crash before terminal commit | Replay may re-infer; no partial business effect |
| Crash after commit, before sending | Existing result reused; reply survives |
| Twilio response lost | Marked unknown; order unchanged |
| Two confirmations of one order | One invoice, one stock deduction |
| Two orders competing for stock | Stock never negative; loser has no partial invoice |
| Correction then confirm of stale quote | Rejected |
| Hold → approve/reject → repeat | One legal transition, no duplicate effects |
| Wrong tenant/customer order ID | Rejected |
| Runtime task exception | Retried or flagged, no restart required |
| n8n notify failure | Held order still visible/actionable on owner page |

8 recorded language/task cases: English + Hinglish feasible, negation, budget/quantity corrections, insufficient stock, hard-constraint conflict, an attempted prompt-injection-style instruction to ignore prices/scope. Check stored outcomes, not just replies.

**Release gate: no unauthorized mutation, duplicate invoice, or negative stock across all required checks.**

---

## K. Build Schedule (10:00 AM – 6:00 PM)

| Time | Deliverable |
|---|---|
| 10:00–10:40 | Provision Neon, deploy one-process backend, core tables, signature-validated webhook, basic dispatcher + sender, one reply through outbox end-to-end |
| 10:40–10:50 | Screen one tool-calling model against the fixture; one fallback only if it fails |
| 10:50–12:30 | Terminal transactions, immutable quotes, validation, CAS confirmation, holds, tenant/customer auth |
| 12:30–1:00 | Wire read/select/propose loop + canonical quote rendering |
| 1:00–2:00 | Lunch + mentor review |
| **2:00–2:45** | **Gate:** real WhatsApp proposal → explicit confirm → invoice → outbox reply, working end-to-end; verify duplicate-input replay produces no duplicate order. Minimal tool-event view. If this fails, stop and fix — nothing else proceeds. |
| 2:45–3:15 | Hinglish cases wired in; owner page for offline stock + held orders |
| 3:15–3:25 | Optional: n8n best-effort notification hook — **stop at 10 minutes if the destination isn't working cleanly**, owner queue remains the review mechanism either way |
| 3:25–4:00 | Required: transaction/replay/authorization/recovery checks from section J |
| 4:00–4:30 | 3-person proxy exercise (or labelled dev self-test) |
| 4:30–4:55 | Fix observed failures, rerun affected checks |
| 4:55–5:10 | Assemble evidence panel: task results, latency, costs, limitations |
| 5:10–5:30 | Rehearse 3-minute pitch + live flow |
| 5:30–6:00 | Submission, deployment freeze, final phone/network check |

**If n8n doesn't fit in its 10-minute window, cut it — the owner queue alone is fully sufficient, and the proxy evidence is what's actually earning the score, not the sponsor integration.**

---

## L. Evidence Panel (one FastAPI page)
Shows: normalized constraints, actual candidate rows, model-selected quantities, validation result, quote/order ID + status, stock before/after, outbox state, observed latency/cost, proxy results with stated limitations. Real tool events and results — never claimed private reasoning. Same protected page exposes owner stock controls, held orders, uncertain sends.

## M. Three-Minute Demo
| Time | Action |
|---|---|
| 0:00–0:25 | State the narrow problem hypothesis; name the evidence as proxy, not merchant |
| 0:25–0:45 | Show catalog + a recorded offline stock change |
| 0:45–1:40 | Send the Hinglish budget/quantity request; show real candidate retrieval + selected basket |
| 1:40–2:10 | Confirm the quote; show invoice + stock update |
| 2:10–2:40 | Show proxy results, measured latency/cost, one verified replay result |
| 2:40–3:00 | State deployment/evidence limits; name the next step as a merchant pilot |

If latency overruns: drop the contrasting case, not the core flow. No live restart. Any fallback recording is explicitly labelled as recorded.

## N. Pitch Framing
> "We're testing whether a small stationery shop can handle budget-constrained WhatsApp orders without manually searching every combination. The customer can mix Hindi and English, specify a budget and product requirements, and approve a basket drawn from current stock. The agent selects the basket; the backend checks every requirement and records the order safely. We tested the workflow with [N] proxies — not merchants — and observed [results]. Stock updates are manual today, and the next step is a merchant pilot."

Don't claim tool-use itself is novel — Meta already markets business agents that take actions. The differentiation is this specific demonstrated workflow and its evidence, not "other bots are decision trees."

## O. Scaling Claim
> "Data and authorization are tenant-scoped. This prototype intentionally runs one process; production throughput and merchant onboarding are not established." Next scaling work: durable worker coordination, sender onboarding, real inventory integration, measured cost at volume. A pooled DB connection and two seeded businesses are not proof of national scale — don't oversell them as such.

---

## Known Remaining Risk (not fixable by more planning)
Model reliability on the basket-selection task under real conditions, actual WhatsApp round-trip latency, whether the proxies genuinely show a time/error benefit, and real merchant appetite. These resolve only through building and testing on the day — projected score is 82/100 conditional on the proxy exercise, code-switched flow, and correctness checks producing the stated evidence.
