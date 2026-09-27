"""
Ordered inbox dispatcher (Section H).

"In-process lock registry, shared by live intake and recovery, processes
each conversation's pending input in order."

The dispatcher pulls 'received' rows ordered by sequence, acquires the
session's in-process lock, and calls run_terminal_action with the
appropriate business action. For this block: echo reply. Later blocks
swap in the real model agent turn.
"""
import asyncio
import logging
import traceback

from app.db import get_conn
from app.transactions import run_terminal_action

log = logging.getLogger(__name__)

# Per-session lock registry — shared by live intake and recovery
_session_locks: dict[str, asyncio.Lock] = {}

MAX_ATTEMPTS = 3
BACKOFF_SECONDS = [2, 5, 15]


def _get_session_lock(session_id: str) -> asyncio.Lock:
    if session_id not in _session_locks:
        _session_locks[session_id] = asyncio.Lock()
    return _session_locks[session_id]


async def enqueue_dispatch(input_id: str, session_id: str, business_id: str) -> None:
    """Fire-and-forget entry point called by the webhook after persisting
    an inbox row. Acquires the session lock so conversation order is
    preserved, then processes."""
    lock = _get_session_lock(session_id)
    async with lock:
        await _process_one(input_id, session_id, business_id)


async def dispatch_pending() -> None:
    """Startup/recovery: pull all 'received' inbox rows ordered by sequence
    and dispatch them. Used by recovery.requeue_interrupted."""
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT input_id, session_id, business_id
            FROM inbox
            WHERE status = 'received'
            ORDER BY sequence
            """
        ).fetchall()

    for input_id, session_id, business_id in rows:
        session_id = str(session_id)
        lock = _get_session_lock(session_id)
        async with lock:
            await _process_one(input_id, session_id, business_id)


async def _process_one(input_id: str, session_id: str, business_id: str) -> None:
    """Process a single inbox row through the terminal-action pattern.
    Bounded retry with backoff; after MAX_ATTEMPTS, mark 'attention'."""

    # Mark processing
    with get_conn() as conn:
        with conn.transaction():
            row = conn.execute(
                """
                UPDATE inbox SET status = 'processing', attempts = attempts + 1
                WHERE input_id = %s AND status IN ('received', 'processing')
                RETURNING attempts, body
                """,
                (input_id,),
            ).fetchone()

    if row is None:
        log.info("Skipping %s — already completed or missing", input_id)
        return

    attempt = row[0]
    body = row[1]

    try:
        # --- Business action: for this block, echo reply ---
        # Later blocks will replace this with run_agent_turn()
        body_text = body.get("text", "") if isinstance(body, dict) else str(body)
        reply_text = f"[echo] Received: {body_text}"

        # Look up destination phone from session
        with get_conn() as conn:
            session_row = conn.execute(
                "SELECT customer_phone FROM sessions WHERE session_id = %s",
                (session_id,),
            ).fetchone()
        customer_phone = session_row[0] if session_row else ""

        reply_payload = {
            "to": customer_phone,
            "text": reply_text,
        }

        # Run the real terminal action pattern
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            run_terminal_action,
            input_id,
            session_id,
            business_id,
            "echo",
            None,  # no business-side effect for echo
            reply_payload,
        )
        log.info("Dispatched %s → %s", input_id, result)

    except Exception:
        error_msg = traceback.format_exc()
        log.exception("Error processing %s (attempt %d)", input_id, attempt)

        if attempt >= MAX_ATTEMPTS:
            # Mark attention — never silently stuck in processing
            with get_conn() as conn:
                with conn.transaction():
                    conn.execute(
                        """
                        UPDATE inbox SET status = 'attention', last_error = %s
                        WHERE input_id = %s
                        """,
                        (error_msg[-500:], input_id),
                    )
            log.error("Gave up on %s after %d attempts — marked attention",
                      input_id, attempt)
        else:
            # Reset to received for retry
            backoff = BACKOFF_SECONDS[min(attempt - 1, len(BACKOFF_SECONDS) - 1)]
            with get_conn() as conn:
                with conn.transaction():
                    conn.execute(
                        """
                        UPDATE inbox SET status = 'received', last_error = %s,
                            next_attempt_at = now() + interval '%s seconds'
                        WHERE input_id = %s
                        """,
                        (error_msg[-500:], backoff, input_id),
                    )
            log.warning("Will retry %s in %ds", input_id, backoff)
