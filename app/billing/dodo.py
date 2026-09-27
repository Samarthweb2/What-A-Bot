import logging
from fastapi import APIRouter, HTTPException

log = logging.getLogger(__name__)
router = APIRouter(tags=["billing"])

@router.post("/businesses/{id}/billing/checkout")
async def create_checkout(id: str):
    raise HTTPException(status_code=501, detail="Not implemented: Create checkout route pending implementation by Jagdeep.")

@router.get("/businesses/{id}/billing/status")
async def get_billing_status(id: str):
    raise HTTPException(status_code=501, detail="Not implemented: Get billing status route pending implementation by Jagdeep.")

@router.post("/webhook/dodo")
async def dodo_webhook():
    raise HTTPException(status_code=501, detail="Not implemented: Dodo webhook route pending implementation by Jagdeep.")
