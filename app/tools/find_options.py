"""Section E tool contract -- signature is fixed, implement the body."""
from typing import Literal


def find_options(
    quantity: int, budget_paise: int,
    ruling: Literal["ruled", "unruled"], size: Literal["A4", "A5"],
    allow_mixed_brands: bool,
    # + injected backend context: business_id, session_id, input_id
):
    """
    Returns INDIVIDUAL eligible candidates only -- never a precomputed
    winning basket. Never claims infeasibility just because the model
    hasn't found a solution. Stores the normalized constraints behind an
    opaque candidate_set_id, bound to the current input/session/business,
    for propose_order to resolve server-side later.
    """
    raise NotImplementedError
