"""Toy scaffold comparison; it is not a GAIA or model evaluation."""
from __future__ import annotations

import json
import random
from pathlib import Path


TASKS = [(2 + i % 4, i % 3 == 0) for i in range(90)]  # (steps, injected failure)


def solve(name: str, steps: int, inject_error: bool, rng: random.Random) -> tuple[bool, bool, int]:
    """Return success, recovery, and tool calls under a fixed stochastic task set."""
    calls = 0
    recovered = not inject_error
    for step in range(steps):
        calls += 1
        if inject_error and step == steps // 2:
            if name == "reactive":
                recovered = rng.random() < 0.35
                calls += 2  # retry and an exploratory check
            elif name == "planner_actor_rater":
                recovered = rng.random() < 0.82
                calls += 1  # rater routes one targeted repair
            else:
                recovered = rng.random() < 0.68
                calls += 1  # executor follows the remaining written plan
    base = {"reactive": 0.91, "planner_actor_rater": 0.92, "planner_then_executor": 0.90}[name]
    success = recovered and rng.random() < base
    return success, recovered, calls


def run() -> dict:
    rows = {}
    for offset, name in enumerate(("reactive", "planner_actor_rater", "planner_then_executor")):
        rng = random.Random(20260904 + offset)
        outcomes = [solve(name, steps, error, rng) for steps, error in TASKS]
        failed = [outcome for outcome, task in zip(outcomes, TASKS) if task[1]]
        rows[name] = {
            "success_rate": round(sum(x[0] for x in outcomes) / len(outcomes), 3),
            "recovery_after_injected_error": round(sum(x[1] for x in failed) / len(failed), 3),
            "mean_tool_calls": round(sum(x[2] for x in outcomes) / len(outcomes), 2),
        }
    return {
        "note": "合成した多段タスクの決定的な玩具実験。GAIA、LLM、論文の数値は再現していない。",
        "experiments": [{"name": "同一タスク上の scaffold 比較", "dataset": "synthetic 90 tasks", "n": 90, "seed": 20260904, "metrics": rows}],
        "boundary": "構造化した制御で注入済みエラーの回復と呼び出し量が変わる、という機構の例示だけを検証する。",
    }


if __name__ == "__main__":
    output = run()
    Path(__file__).with_name("results.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))
