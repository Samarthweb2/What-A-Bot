"""
Protected owner page (Sections G/L). Auth via OWNER_PAGE_TOKEN.

Required surfaces:
  - stock adjustments (manual offline-stock-update path, Section B.2 --
    "record a sale / correct a count, shows last-updated time")
  - held-order approve/reject (calls holds.owner_resolve_hold)
  - trace / failed-work ('attention') / uncertain-sends ('unknown') view

Stock updates are owner-only, validated, audited via `events` -- the
customer-facing agent has no inventory-editing tool (Section G).
"""
from fastapi import APIRouter

router = APIRouter(prefix="/owner")


@router.get("/")
async def owner_dashboard():
    # TODO: render owner.html with held orders, attention/unknown items,
    # current catalog + last-updated times
    raise NotImplementedError


@router.post("/stock/{business_id}/{sku}")
async def adjust_stock(business_id: str, sku: str):
    # TODO: validated manual stock adjustment, audited via `events`
    raise NotImplementedError


@router.post("/holds/{order_id}/approve")
async def approve_hold(order_id: str):
    raise NotImplementedError


@router.post("/holds/{order_id}/reject")
async def reject_hold(order_id: str):
    raise NotImplementedError
