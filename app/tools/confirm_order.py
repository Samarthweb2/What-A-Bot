"""Section E tool contract -- signature is fixed, implement the body."""


def confirm_order(order_id: str):
    """
    Requires an explicit customer command (e.g. "CONFIRM Q7K2"). Backend
    resolves the quote and injects authorization -- never model-invented.
    Checks session, tenant, expiry, status, stock, current price. Returns
    the existing result if already resolved (idempotent). Can be routed
    deterministically -- no unnecessary model call just to look more
    agentic.

    Returns one of: Confirmed | Held | StaleQuote | AlreadyResolved
    """
    raise NotImplementedError
