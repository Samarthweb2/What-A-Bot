"""
Section I: exhaustive-enumeration test harness for the fixture catalog.
This is TEST-ONLY logic -- never the agent's runtime path. Verifies the
three stock-level results in tests/fixtures/catalog.json
(expected_by_stock_A).

NOTE: per the coordination plan, this file is meant to be drafted by the
Antigravity 2.0 desktop agent in parallel with IDE's morning work (it only
needs this fixture data, not the live app) -- paste its output here.
"""
import json
import itertools

with open("tests/fixtures/catalog.json") as f:
    FIXTURE = json.load(f)


def test_exhaustive_enumeration_matches_expected():
    task = FIXTURE["flagship_task"]
    expected = FIXTURE["expected_by_stock_A"]

    for stock_A_str, expected_result in expected.items():
        stock_A = int(stock_A_str)
        # Filter items that match size and ruling
        eligible_items = []
        for item in FIXTURE["items"]:
            if item["size"] == task["size"] and item["ruling"] == task["ruling"]:
                # Override stock for item A
                qty = stock_A if item["sku"] == "A" else item["qty"]
                eligible_items.append({"sku": item["sku"], "price": item["unit_price_paise"], "qty": qty})

        # We have A, B, C. Let's brute-force the combinations of quantities.
        item_A = next(i for i in eligible_items if i["sku"] == "A")
        item_B = next(i for i in eligible_items if i["sku"] == "B")
        item_C = next(i for i in eligible_items if i["sku"] == "C")

        feasible_baskets = []
        min_cost = float('inf')

        for a in range(item_A["qty"] + 1):
            for b in range(item_B["qty"] + 1):
                for c in range(item_C["qty"] + 1):
                    if a + b + c == task["quantity"]:
                        cost = a * item_A["price"] + b * item_B["price"] + c * item_C["price"]
                        min_cost = min(min_cost, cost)
                        if cost <= task["budget_paise"]:
                            feasible_baskets.append({"A": a, "B": b, "C": c, "cost": cost})

        if expected_result["feasible_baskets"] == 0:
            assert len(feasible_baskets) == 0
            assert min_cost == expected_result["min_cost_for_12_paise"]
        else:
            assert len(feasible_baskets) == expected_result["feasible_baskets"]
            assert min_cost == expected_result["min_cost_paise"]
            if "basket" in expected_result:
                # Find the basket that matches
                b = expected_result["basket"]
                found = next(fb for fb in feasible_baskets if fb["A"] == b["A"] and fb["B"] == b["B"] and fb["C"] == b["C"])
                assert found is not None
