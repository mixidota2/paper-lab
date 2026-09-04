"""Toy scaffold comparison: three loop policies on synthetic tasks with mid-trajectory failures.

Illuminates the paper's behavioral claim that structured scaffolds use fewer actions
and recover more often from mid-trajectory errors — not GAIA accuracy itself.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

SEED = 42
N_TASKS = 200
FAIL_INJECT_P = 0.35  # probability a tool step fails mid-trajectory


def _task_difficulty(rng: random.Random) -> int:
    """Steps needed under an ideal policy (2–8)."""
    return rng.randint(2, 8)


def run_react(difficulty: int, rng: random.Random) -> dict:
    """Interleaved reason-act: explores more, recovers poorly after failure."""
    actions = 0
    failed = False
    recovered = False
    success = False
    budget = difficulty * 4
    progress = 0
    while actions < budget and progress < difficulty:
        actions += 1
        # Inject mid-trajectory tool failure
        if progress > 0 and not failed and rng.random() < FAIL_INJECT_P:
            failed = True
            continue
        if failed:
            # Reactive loop often retries the same failing action
            if rng.random() < 0.25:
                recovered = True
                failed = False
                progress += 1
            continue
        # Nominal progress with some wasted probes
        if rng.random() < 0.55:
            progress += 1
    success = progress >= difficulty
    return {
        "actions": actions,
        "failed": failed or recovered or (progress > 0 and actions > difficulty),
        "mid_fail": int(failed or recovered),
        "recovered": int(recovered and success),
        "success": int(success),
    }


def run_par(difficulty: int, rng: random.Random) -> dict:
    """Planner-Actor-Rater: fewer actions; rater can re-route after failure."""
    actions = 0
    failed = False
    recovered = False
    success = False
    budget = difficulty * 3
    progress = 0
    while actions < budget and progress < difficulty:
        actions += 1
        if progress > 0 and not failed and rng.random() < FAIL_INJECT_P:
            failed = True
            continue
        if failed:
            # Rater flags failure and planner revises → higher recovery
            if rng.random() < 0.70:
                recovered = True
                failed = False
                progress += 1
            continue
        if rng.random() < 0.80:
            progress += 1
    success = progress >= difficulty
    return {
        "actions": actions,
        "mid_fail": int(failed or recovered),
        "recovered": int(recovered and success),
        "success": int(success),
    }


def run_planner_executor(difficulty: int, rng: random.Random) -> dict:
    """Planner-then-executor: plan once, execute; fewest actions; decent recovery."""
    actions = 1  # planning step (no tools)
    failed = False
    recovered = False
    success = False
    budget = difficulty * 2 + 1
    progress = 0
    while actions < budget and progress < difficulty:
        actions += 1
        if progress > 0 and not failed and rng.random() < FAIL_INJECT_P:
            failed = True
            continue
        if failed:
            # Explicit plan may survive a failed step
            if rng.random() < 0.55:
                recovered = True
                failed = False
                progress += 1
            continue
        if rng.random() < 0.85:
            progress += 1
    success = progress >= difficulty
    return {
        "actions": actions,
        "mid_fail": int(failed or recovered),
        "recovered": int(recovered and success),
        "success": int(success),
    }


POLICIES = {
    "react": run_react,
    "planner_actor_rater": run_par,
    "planner_then_executor": run_planner_executor,
}


def main() -> dict:
    rng = random.Random(SEED)
    tasks = [_task_difficulty(rng) for _ in range(N_TASKS)]
    experiments = []
    for name, fn in POLICIES.items():
        rows = [fn(d, rng) for d in tasks]
        mid = [r for r in rows if r["mid_fail"]]
        recovery_rate = (
            sum(r["recovered"] for r in mid) / len(mid) if mid else 0.0
        )
        metrics = {
            "mean_actions": round(sum(r["actions"] for r in rows) / len(rows), 3),
            "success_rate": round(sum(r["success"] for r in rows) / len(rows), 3),
            "mid_trajectory_fail_rate": round(len(mid) / len(rows), 3),
            "recovery_given_mid_fail": round(recovery_rate, 3),
        }
        experiments.append(
            {
                "name": f"toy_scaffold_{name}",
                "dataset": "synthetic_tool_tasks_v0",
                "n": N_TASKS,
                "seed": SEED,
                "policy": name,
                "metrics": metrics,
            }
        )

    # Cross-policy deltas vs ReAct (illustrative mechanism signal)
    by_name = {e["policy"]: e["metrics"] for e in experiments}
    react = by_name["react"]
    summary = {
        "action_ratio_par_vs_react": round(
            by_name["planner_actor_rater"]["mean_actions"] / react["mean_actions"], 3
        ),
        "action_ratio_s3_vs_react": round(
            by_name["planner_then_executor"]["mean_actions"] / react["mean_actions"], 3
        ),
        "recovery_lift_par_vs_react_pp": round(
            (
                by_name["planner_actor_rater"]["recovery_given_mid_fail"]
                - react["recovery_given_mid_fail"]
            )
            * 100,
            1,
        ),
        "recovery_lift_s3_vs_react_pp": round(
            (
                by_name["planner_then_executor"]["recovery_given_mid_fail"]
                - react["recovery_given_mid_fail"]
            )
            * 100,
            1,
        ),
    }

    payload = {
        "note": (
            "Synthetic toy only. Does not reproduce GAIA accuracy, model families, "
            "or the paper's 28pp scaffold gap. Mechanism-oriented: action count and "
            "mid-trajectory recovery under three loop policies."
        ),
        "fictional": False,
        "toy": True,
        "paper_claims_not_tested": [
            "GAIA L1/L2 accuracy gaps",
            "H1–H4 pre-registered hypothesis tests",
            "model-family conditioning of multi-agent advantage",
            "cost-per-correct rankings (e.g. Gemini s3)",
        ],
        "summary": summary,
        "experiments": experiments,
    }
    out = Path(__file__).resolve().parent / "results.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return payload


if __name__ == "__main__":
    main()
