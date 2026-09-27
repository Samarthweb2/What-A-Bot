"""
Evidence panel (Section L) -- one FastAPI page. Shows: normalized
constraints, actual candidate rows, model-selected quantities, validation
result, quote/order ID + status, stock before/after, outbox state,
observed latency/cost, proxy results with stated limitations. Real tool
events and results -- never claimed private reasoning.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/evidence")


@router.get("/")
async def evidence_panel():
    # TODO: render evidence.html from the `events` table + latest orders
    raise NotImplementedError
