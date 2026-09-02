#!/usr/bin/env python3
"""Calculate mystery bounty tournament values from extracted screenshot numbers."""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP


def dec(value) -> Decimal:
    return Decimal(str(value).replace(",", ""))


def q(value: Decimal, places: str = "0.01") -> str:
    return str(value.quantize(Decimal(places), rounding=ROUND_HALF_UP))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="JSON object with bounties and tournament fields")
    parser.add_argument("--input-file", help="Path to a JSON input file")
    args = parser.parse_args()
    if args.input_file:
        with open(args.input_file, "r", encoding="utf-8") as f:
            raw = f.read()
    elif args.input:
        raw = args.input
    else:
        raw = sys.stdin.read()
    data = json.loads(raw)

    bounties = data["bounties"]
    bounty_total = sum(dec(x["amount"]) * dec(x["remaining"]) for x in bounties)
    bounty_count = sum(int(x["remaining"]) for x in bounties)
    avg_bounty_cash = bounty_total / Decimal(bounty_count) if bounty_count else Decimal(0)

    prize_pool = dec(data["prize_pool"])
    if "total_entries" in data and "starting_stack" in data:
        total_chips = dec(data["total_entries"]) * dec(data["starting_stack"])
        chip_basis = "entries_x_starting_stack"
    else:
        total_chips = dec(data["remaining_players"]) * dec(data["avg_stack"])
        chip_basis = "remaining_players_x_avg_stack_estimate"

    chips_per_cash = total_chips / prize_pool if prize_pool else Decimal(0)
    avg_bounty_chips = avg_bounty_cash * chips_per_cash

    result = {
        "remaining_bounty_count": bounty_count,
        "remaining_bounty_cash_total": q(bounty_total),
        "average_bounty_cash": q(avg_bounty_cash),
        "total_chips": q(total_chips),
        "chip_basis": chip_basis,
        "chips_per_1_cash": q(chips_per_cash),
        "average_bounty_chips": q(avg_bounty_chips),
    }

    if data.get("current_big_blind"):
        current_bb = avg_bounty_chips / dec(data["current_big_blind"])
        result["average_bounty_current_bb"] = q(current_bb)
    if data.get("next_big_blind"):
        next_bb = avg_bounty_chips / dec(data["next_big_blind"])
        result["average_bounty_next_bb"] = q(next_bb)
    if data.get("hero_stack_bb"):
        hero_chips = dec(data["hero_stack_bb"]) * dec(data["current_big_blind"])
        result["hero_stack_chips"] = q(hero_chips)
        result["bounty_as_hero_stack_ratio"] = q(avg_bounty_chips / hero_chips)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
