"""Section E tool contract -- signature is fixed, implement the body."""
from typing import Literal


def finish_reply(kind: Literal["clarification", "faq", "needs_owner"], text: str):
    """Returns PersistedReply."""
    raise NotImplementedError
