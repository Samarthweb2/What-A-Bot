"""
Startup recovery (Section H):
  - requeue interrupted 'processing' rows
  - leave committed outcomes untouched
  - leave pending outbox entries alone
  - mark interrupted 'sending' rows 'unknown'
"""
import logging

from app.db import get_conn

log = logging.getLogger(__name__)


def requeue_interrupted() -> None:
    """Run once at startup to recover from a crash/restart."""
    with get_conn() as conn:
        with conn.transaction():
            # Requeue interrupted processing — they'll be re-dispatched
            result1 = conn.execute(
                "UPDATE inbox SET status = 'received' WHERE status = 'processing'"
            )
            requeued = result1.rowcount

            # Mark interrupted sending as unknown — owner decides retry
            result2 = conn.execute(
                "UPDATE outbox SET state = 'unknown' WHERE state = 'sending'"
            )
            marked = result2.rowcount

    if requeued or marked:
        log.warning(
            "Startup recovery: requeued %d processing inbox rows, "
            "marked %d sending outbox rows unknown",
            requeued, marked,
        )
    else:
        log.info("Startup recovery: nothing to recover")
