"""
Telegram Bot API webhook (Section C).

Flow required by the plan:
  1. Validate the Telegram secret token.
  2. Persist the inbound event + bind the tenant (business_id) via the
     sessions table.
  3. Acknowledge immediately with a 200 OK response.
  4. Never wait on the model or the conversation lock here -- Section H:
     "Webhook intake never waits on the model or the conversation lock."

input_id must be 'tg:<message_id>', never model-supplied (Section D).
"""
import asyncio
import json
import logging

from fastapi import APIRouter, Request, Response, HTTPException

from app.config import settings
from app.db import get_conn

log = logging.getLogger(__name__)

router = APIRouter()

# Default business for this block — multi-tenant routing is a later concern.
DEFAULT_BUSINESS_ID = "test_shop"

@router.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    raw_body = await request.body()
    
    # --- 1. Validate secret token ---
    secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret_token != settings.telegram_webhook_secret:
        log.warning("Invalid Telegram secret token — rejecting")
        raise HTTPException(status_code=403, detail="Invalid token")

    # --- 2. Parse JSON payload ---
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Handle incoming messages
    if "message" in payload:
        message = payload["message"]
        message_id = message.get("message_id")
        chat = message.get("chat", {})
        chat_id = chat.get("id")
        
        # Only handle text messages for now
        body_text = message.get("text", "")

        if not message_id or not chat_id:
            log.warning("Missing message id or chat id")
            return Response(status_code=200, content="OK")

        # Use string representation of chat_id for database consistency
        from_number = str(chat_id)
        to_number = "telegram_bot"  # Default destination identifier

        input_id = f"tg:{message_id}"

        # --- 3. Upsert session + insert inbox (short transaction) ---
        with get_conn() as conn:
            with conn.transaction():
                # Upsert session: (customer_phone, destination) -> session row
                row = conn.execute(
                    """
                    INSERT INTO sessions (customer_phone, destination, active_business_id)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (customer_phone, destination) DO UPDATE
                        SET active_business_id = EXCLUDED.active_business_id
                    RETURNING session_id, active_business_id
                    """,
                    (from_number, to_number, DEFAULT_BUSINESS_ID),
                ).fetchone()
                session_id = str(row[0])
                business_id = row[1]

                # Insert inbox — ON CONFLICT DO NOTHING for retries
                conn.execute(
                    """
                    INSERT INTO inbox (input_id, source, session_id, business_id,
                                       body, status)
                    VALUES (%s, 'telegram', %s, %s, %s, 'received')
                    ON CONFLICT (input_id) DO NOTHING
                    """,
                    (input_id, session_id, business_id,
                     json.dumps({"text": body_text})),
                )

        # --- 4. Fire-and-forget dispatch (don't await model here) ---
        from app.dispatcher import enqueue_dispatch
        asyncio.get_event_loop().call_soon(
            lambda i=input_id, s=session_id, b=business_id: asyncio.ensure_future(enqueue_dispatch(i, s, b))
        )

        log.info("Accepted inbound %s from chat %s", input_id, from_number)

    # --- 5. Acknowledgment ---
    return Response(status_code=200, content="OK")
