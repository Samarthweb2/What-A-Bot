import logging
from fastapi import APIRouter, HTTPException

log = logging.getLogger(__name__)
router = APIRouter(tags=["bot_link"])

@router.post("/businesses/{id}/bot-link")
async def create_bot_link(id: str):
    raise HTTPException(status_code=501, detail="Not implemented: Bot link creation route pending implementation by Nikhil.")

def issue_token(business_id: str, owner_id: str) -> str:
    raise NotImplementedError("bot_link.issue_token not implemented")

def consume_token(token: str, chat_id: int):
    raise NotImplementedError("bot_link.consume_token not implemented")
