# Frozen API Contract (frozen at 1:15 PM)

| Route | Method | Auth | Request | Response | Notes |
|---|---|---|---|---|---|
| `/auth/login` | POST | none | `{email, password}` | `{token}` or 401 | seeded owner accounts |
| `/auth/me` | GET | Bearer | — | `{owner_id, email, businesses: [business_id]}` | |
| `/businesses` | GET | Bearer | — | `[{business_id, name, business_type}]` | only owner's memberships |
| `/businesses/{id}/bot-link` | POST | Bearer, must own `{id}` | — | `{token, deep_link_url, expires_at}` | single-use, 10 min expiry |
| `/businesses/{id}/catalog` | GET | Bearer | — | `[{sku, name, brand, ruling, size, price_paise, qty}]` | retail only |
| `/businesses/{id}/services` | GET | Bearer | — | `[{service_id, name, duration_minutes, price_paise}]` | service only |
| `/businesses/{id}/slots` | GET | Bearer | `?service_id=` | `[{slot_id, starts_at, capacity}]` | |
| `/businesses/{id}/orders` | GET | Bearer | `?status=` | `[{order_id, status, total_paise, ...}]` | read-only, confirmation stays a Telegram action |
| `/businesses/{id}/holds` | GET/POST | Bearer | POST: `{order_id, approve: bool}` | order/booking row | owner approve/reject |
| `/businesses/{id}/evidence` | GET | Bearer | — | trace + latency/cost fields | never claimed private reasoning |
| `/businesses/{id}/billing/checkout` | POST | Bearer | — | `{checkout_url}` | Dodo hosted checkout |
| `/businesses/{id}/billing/status` | GET | Bearer | — | `{plan, updated_at}` | |
| `/webhook/telegram` | POST | secret header | Telegram Update | 200 | existing, unchanged |
| `/webhook/dodo` | POST | signature | Dodo event | 200 | new, isolated, never touches orders/bookings |

Error envelope, all routes: `{"error": {"code": str, "message": str}}`, matching HTTP status. 
Money: integer paise everywhere, same as existing convention. 
Timestamps: stored/transmitted UTC ISO-8601; displayed in Asia/Kolkata on frontend only.
