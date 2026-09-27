-- Transcribed from plan.md Section D. The plan explicitly notes this is a
-- specification, not executable SQL as written there, and that NOT NULL /
-- CHECK constraints need to be added explicitly. That's done below as a
-- draft -- IDE agent: verify each constraint against Section D's prose
-- before trusting this, especially the state-machine trigger at the bottom.

CREATE TABLE businesses (
    business_id         TEXT PRIMARY KEY,
    name                TEXT NOT NULL,
    review_above_paise  INTEGER NOT NULL CHECK (review_above_paise >= 0),
    faq                 JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE catalog (
    business_id       TEXT NOT NULL REFERENCES businesses(business_id),
    sku               TEXT NOT NULL,
    name              TEXT NOT NULL,
    brand             TEXT NOT NULL,
    ruling            TEXT NOT NULL CHECK (ruling IN ('ruled', 'unruled')),
    size              TEXT NOT NULL CHECK (size IN ('A4', 'A5')),
    unit_price_paise  INTEGER NOT NULL CHECK (unit_price_paise > 0),
    qty               INTEGER NOT NULL CHECK (qty >= 0),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (business_id, sku)
);

CREATE TABLE sessions (
    session_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_phone      TEXT NOT NULL,
    destination         TEXT NOT NULL,
    active_business_id  TEXT REFERENCES businesses(business_id),
    UNIQUE (customer_phone, destination)
);

CREATE TABLE inbox (
    input_id        TEXT PRIMARY KEY,   -- 'wa:<MessageSid>' or 'owner:<nonce>', never model-supplied
    sequence        BIGSERIAL UNIQUE,
    source          TEXT NOT NULL CHECK (source IN ('whatsapp', 'owner')),
    session_id      UUID REFERENCES sessions(session_id),
    business_id     TEXT REFERENCES businesses(business_id),
    body            JSONB NOT NULL,
    status          TEXT NOT NULL CHECK (status IN ('received', 'processing', 'completed', 'attention')),
    attempts        INTEGER NOT NULL DEFAULT 0,
    next_attempt_at TIMESTAMPTZ,
    last_error      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE orders (
    order_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quote_code       TEXT UNIQUE NOT NULL,
    origin_input_id  TEXT UNIQUE NOT NULL REFERENCES inbox(input_id),
    session_id       UUID NOT NULL REFERENCES sessions(session_id),
    business_id      TEXT NOT NULL REFERENCES businesses(business_id),
    status           TEXT NOT NULL CHECK (status IN ('draft', 'held', 'confirmed', 'cancelled')),
    constraints      JSONB NOT NULL,
    items            JSONB NOT NULL,     -- immutable after creation
    total_paise      INTEGER NOT NULL CHECK (total_paise >= 0),
    expires_at       TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (business_id, order_id)
);

CREATE TABLE invoices (
    order_id    UUID PRIMARY KEY REFERENCES orders(order_id),
    invoice_id  UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    payload     JSONB NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE message_outcomes (
    input_id    TEXT PRIMARY KEY REFERENCES inbox(input_id),
    order_id    UUID REFERENCES orders(order_id),
    kind        TEXT NOT NULL,
    result      JSONB NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE outbox (
    outbox_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_key        TEXT UNIQUE NOT NULL,
    input_id         TEXT REFERENCES message_outcomes(input_id),
    session_id       UUID REFERENCES sessions(session_id),
    business_id      TEXT REFERENCES businesses(business_id),
    payload          JSONB NOT NULL,
    state            TEXT NOT NULL CHECK (state IN ('pending', 'sending', 'accepted', 'unknown', 'failed')),
    attempt_no       INTEGER NOT NULL DEFAULT 0,
    twilio_sid       TEXT,
    delivery_status  TEXT,
    next_attempt_at  TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE events (
    event_id    BIGSERIAL PRIMARY KEY,
    input_id    TEXT,
    kind        TEXT NOT NULL,
    data        JSONB NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Order state machine (Section D): draft -> confirmed|held|cancelled ;
-- held -> confirmed|cancelled ; confirmed/cancelled terminal.
-- Trigger rejects any other transition AND rejects edits to immutable
-- fields (items, constraints, total_paise) once a row exists.

CREATE OR REPLACE FUNCTION enforce_order_state_machine()
RETURNS TRIGGER AS $$
BEGIN
    -- Reject edits to immutable fields
    IF NEW.items IS DISTINCT FROM OLD.items THEN
        RAISE EXCEPTION 'Cannot modify immutable field: items';
    END IF;
    IF NEW.constraints IS DISTINCT FROM OLD.constraints THEN
        RAISE EXCEPTION 'Cannot modify immutable field: constraints';
    END IF;
    IF NEW.total_paise IS DISTINCT FROM OLD.total_paise THEN
        RAISE EXCEPTION 'Cannot modify immutable field: total_paise';
    END IF;

    -- Enforce one-way state transitions
    IF OLD.status = 'draft' AND NEW.status IN ('confirmed', 'held', 'cancelled') THEN
        RETURN NEW;
    ELSIF OLD.status = 'held' AND NEW.status IN ('confirmed', 'cancelled') THEN
        RETURN NEW;
    ELSIF OLD.status = NEW.status THEN
        -- No-op status update is allowed (idempotent)
        RETURN NEW;
    ELSE
        RAISE EXCEPTION 'Invalid order state transition: % -> %', OLD.status, NEW.status;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER orders_state_machine
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION enforce_order_state_machine();

-- ============================================================
-- Seed data: one test business + Section I fixture catalog
-- ============================================================

INSERT INTO businesses (business_id, name, review_above_paise, faq) VALUES
    ('test_shop', 'Sharma Stationery', 100000, '{}')
ON CONFLICT (business_id) DO NOTHING;

INSERT INTO catalog (business_id, sku, name, brand, ruling, size, unit_price_paise, qty) VALUES
    ('test_shop', 'A', 'Classic Ruled A5',   'Classmate', 'ruled',   'A5', 4000, 5),
    ('test_shop', 'B', 'Premium Ruled A5',   'Navneet',   'ruled',   'A5', 5000, 4),
    ('test_shop', 'C', 'Deluxe Ruled A5',    'Sundaram',  'ruled',   'A5', 6000, 5),
    ('test_shop', 'D', 'Basic Unruled A5',   'Classmate', 'unruled', 'A5', 2500, 30)
ON CONFLICT (business_id, sku) DO NOTHING;
