"""Section E tool contract -- signature is fixed, implement the body."""


def propose_order(candidate_set_id: str, items: list[dict]):
    """
    items: list of {"sku": str, "qty": int}

    Resolves the stored constraints behind candidate_set_id server-side --
    NEVER re-trusts the model's restated constraints. REQUIRES the sum of
    selected quantities to equal the requested quantity (without this
    check, a perfectly priced 11-notebook basket could pass for a
    12-notebook request). Also validates budget, size, ruling,
    brand-mixing permission, and CURRENT catalog data. Unknown/missing
    required constraints trigger clarification. Computes price/total
    itself.

    On success: creates the immutable draft AND its outcome/reply,
    atomically (via transactions.run_terminal_action). Terminal action --
    the model loop stops after a successful commit.
    """
    raise NotImplementedError
