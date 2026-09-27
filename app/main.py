"""
FastAPI entrypoint. Wires together the webhook, owner page, and evidence
panel routers, starts the sender loop and the startup recovery pass
(Section H), and exposes the health-check endpoint (Section C).

This file stays thin -- routing and startup/shutdown wiring only.
Business logic belongs in transactions.py / holds.py / tools/.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.webhook import router as webhook_router
from app.db import init_pool, health_ping, pool
from app.recovery import requeue_interrupted
from app.sender import start_sender_loop
from app.dispatcher import dispatch_pending

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    log.info("EmberGround starting up")
    init_pool()
    requeue_interrupted()
    await start_sender_loop()
    # Re-dispatch any rows that were requeued by recovery
    import asyncio
    asyncio.ensure_future(dispatch_pending())
    log.info("EmberGround ready")
    yield
    # --- Shutdown ---
    if pool is not None:
        pool.close()
    log.info("EmberGround shut down")


app = FastAPI(title="EmberGround", lifespan=lifespan)

app.include_router(webhook_router)
# Owner page and evidence panel routers are wired in later blocks:
# from app.owner_page.routes import router as owner_router
# from app.evidence_panel.routes import router as evidence_router
# app.include_router(owner_router)
# app.include_router(evidence_router)


@app.get("/health")
async def health():
    """External DB-touching health check — Section C says run every ~3 min
    to mitigate idle sleep on Render."""
    ok = health_ping()
    if ok:
        return {"status": "ok"}
    return {"status": "error"}, 503
