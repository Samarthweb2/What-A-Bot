"""
Held-order flow and n8n notification (Section G).

Threshold crossed on confirm:
    draft -> held (no stock deducted, no invoice)
    persist customer reply + owner-visible held order
    [transaction commits]
    AFTER commit: best-effort notification to ONE configured n8n webhook

Notification failure must NEVER change the order outcome or block the
customer reply -- the owner queue is the authoritative review mechanism
regardless of whether the ping arrives. The notification contains an
order reference and a link to the owner page -- never approval
credentials. n8n never authorizes anything and never receives a callback.
"""


def draft_to_held(order_id: str, business_id: str, session_id: str) -> dict:
    """Runs inside the same terminal-action transaction as an ordinary
    confirm -- see transactions.run_terminal_action. Sets status='held'
    instead of 'confirmed', skips stock decrement and invoice creation."""
    raise NotImplementedError


async def notify_n8n_hold(order_id: str, business_id: str) -> None:
    """
    Called AFTER the held-order transaction commits -- never inside it.
    Authenticated with N8N_SHARED_SECRET, short timeout. Record
    success/failure in `events`. Swallow failures -- see docstring above.
    """
    raise NotImplementedError


def owner_resolve_hold(order_id: str, business_id: str, approve: bool) -> dict:
    """
    Owner approve/reject on the protected page. Same CAS + transaction
    pattern as customer confirmation, expected_status='held'. Repeat
    actions return the stored/current terminal state (idempotent).
    """
    raise NotImplementedError
