"""
The tool-calling loop: reads catalog, selects an action among the Section E
tools (find_options, propose_order, confirm_order, answer_faq,
finish_reply). Backend context (input_id, session_id, business_id,
customer_phone, authorized_quote_id) is injected -- never a model-editable
argument.

Model selection happens at the 10:40-10:50 build-schedule slot: screen one
tool-calling model against the Section I fixture task, pick ONE fallback
only if it fails. Record both in .env (MODEL_NAME / MODEL_FALLBACK_NAME).

TODO(IDE agent): implement the agent loop -- give the model the tool
schemas from app/tools/*.py, the catalog for business_id, and the
conversation so far; execute whichever tool it calls; propose_order and
confirm_order are terminal (loop stops after a successful commit).
"""


async def run_agent_turn(input_id: str, business_id: str, session_id: str,
                          message_body: dict) -> None:
    raise NotImplementedError
