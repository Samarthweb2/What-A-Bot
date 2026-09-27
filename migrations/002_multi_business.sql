-- migrations/002_multi_business.sql
-- Additive only. Does not touch 001_init.sql's tables/rows. Apply once, after
-- reviewing against the actual current schema.

ALTER TABLE businesses ADD COLUMN business_type TEXT NOT NULL DEFAULT 'retail'
    CHECK (business_type IN ('retail', 'service'));

ALTER TABLE inbox ADD COLUMN telegram_chat_id BIGINT;
ALTER TABLE inbox ADD COLUMN telegram_update_id BIGINT;
ALTER TABLE inbox ADD COLUMN telegram_message_id BIGINT;
-- Fixes known issue #1: input_id becomes 'tg:<bot_id>:<update_id>' (globally
-- unique, not chat-scoped message_id). Store chat/message id separately for tracing.

CREATE TABLE owners (
    owner_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE owner_business_memberships (
    owner_id UUID NOT NULL REFERENCES owners(owner_id),
    business_id TEXT NOT NULL REFERENCES businesses(business_id),
    PRIMARY KEY (owner_id, business_id)
);

CREATE TABLE bot_link_tokens (
    token TEXT PRIMARY KEY,
    business_id TEXT NOT NULL REFERENCES businesses(business_id),
    owner_id UUID NOT NULL REFERENCES owners(owner_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL,
    consumed_at TIMESTAMPTZ,
    consumed_by_chat_id BIGINT
);
-- Single-use: consumed_at IS NULL is the only usable state. Enforce in code
-- via UPDATE ... WHERE consumed_at IS NULL RETURNING token (CAS pattern,
-- same style as order confirmation).

CREATE TABLE services (
    business_id TEXT NOT NULL REFERENCES businesses(business_id),
    service_id TEXT NOT NULL,
    name TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
    price_paise INTEGER NOT NULL CHECK (price_paise > 0),
    PRIMARY KEY (business_id, service_id)
);

CREATE TABLE service_slots (
    slot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id TEXT NOT NULL,
    service_id TEXT NOT NULL,
    starts_at TIMESTAMPTZ NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity >= 0),
    FOREIGN KEY (business_id, service_id) REFERENCES services(business_id, service_id)
);

CREATE TABLE bookings (
    booking_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    origin_input_id TEXT UNIQUE NOT NULL REFERENCES inbox(input_id),
    session_id UUID NOT NULL REFERENCES sessions(session_id),
    business_id TEXT NOT NULL REFERENCES businesses(business_id),
    slot_id UUID NOT NULL REFERENCES service_slots(slot_id),
    status TEXT NOT NULL CHECK (status IN ('draft', 'held', 'confirmed', 'cancelled')),
    total_paise INTEGER NOT NULL CHECK (total_paise >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- Capacity allocation on confirm: same CAS-then-decrement pattern as stock,
-- against service_slots.capacity, inside run_terminal_action.

CREATE TABLE billing_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id TEXT NOT NULL REFERENCES businesses(business_id),
    dodo_event_id TEXT UNIQUE NOT NULL,   -- dedup key
    kind TEXT NOT NULL,
    status TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE business_plan (
    business_id TEXT PRIMARY KEY REFERENCES businesses(business_id),
    plan TEXT NOT NULL DEFAULT 'trial' CHECK (plan IN ('trial', 'test_paid')),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Seed data (Nikhil runs once, idempotent — INSERT ... ON CONFLICT DO NOTHING, never a destructive reset on normal startup):
-- businesses: demo-stationery-1 (retail, existing fixture A/B/C/D unchanged), demo-supermarket-1 (retail, ~6 packaged SKUs, integer package counts), demo-services-1 (service, "UrbanFix-style home services demo", 2–3 services, a handful of slots today/tomorrow).
-- owners: at least 2 seeded accounts — one with membership to all three businesses (for the main demo), one restricted to a single business (to prove isolation, per master prompt §"Demo authentication").
-- Stable, hardcoded IDs everywhere above — never regenerated per run.
-- A separate, explicit scripts/demo_reset.py (dev-only, never called on startup) if a reset is needed mid-afternoon.
