# Integration & Correctness Test Matrix

Original 11 checks (unchanged, still required) plus, new for this scope:

| New check | Required observation |
|---|---|
| Telegram cross-chat IDs / replays | Two different chats never share an inbox identity; a replayed update_id loads its original tenant, doesn't re-derive from new context |
| Ordered retry after 'attention' | A stuck row is visibly recoverable on owner page, not silently lost |
| Tenant switch with queued messages | An in-flight message keeps its original business_id even if the owner switches business in the browser meanwhile |
| Unauthorized business-picker access | Owner without membership gets 403, not an empty-but-technically-200 list |
| Expired / reused bot-link token | Both rejected, with a clear message, no silent no-op |
| Voice transcription failure | Customer gets "please type instead," not a stuck conversation |
| Cross-tenant memory leakage | Business A's Breeth context never appears in Business B's replies |
| Retail stock contention (both businesses) | Never negative, loser gets clean stale-quote |
| Service-slot contention | Same — capacity never negative |
| Stale quote after correction/price change | Rejected, new quote required |
| Duplicate/out-of-order Dodo events | Deduped by event ID, order-independent |
| Payment-return spoofing | Redirect alone changes nothing; only verified webhook status does |
| n8n failure | Held order still fully visible/actionable on owner page regardless |
| Gemini quota failure | Truthful "try again" reply persisted, never a fabricated result |
| Startup recovery | Unchanged from original — still required |

Minimum release gate: authorization (tenant isolation + owner membership), replay safety, invoice/booking correctness, stock/capacity never negative, billing integrity (never touches order state). Everything else is demo polish, not gate-blocking.

Test with mocked failure injection only where explicitly labeled as such — a live sponsor claim in the demo needs a live integration result behind it, not a mock standing in unlabeled.
