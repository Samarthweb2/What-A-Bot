import logging

log = logging.getLogger(__name__)

def update_context(business_id: str, session_id: str, payload: dict) -> None:
    raise NotImplementedError("breeth_adapter.update_context not implemented")

def get_context(business_id: str, session_id: str) -> dict:
    raise NotImplementedError("breeth_adapter.get_context not implemented")
