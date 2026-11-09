# Dated research notes: 2026-10-27-harness-findings

These are historical authored summaries and source-reading limitations. Publication and retrieval dates are those recorded at the time. No new primary verification or experimental reproduction is claimed.

## Actual new primary delta: Harness-Zero checkpoint defaults

**Author-maintainer description:** “Fix default checkpoints for short training runs.”

Primary URLs, retrieved **October26 ~18:09 UTC**:

- https://github.com/metaevo-ai/harness-zero/pull/1 — created2026-10-26 08:31:24 UTC; merged08:31:44 UTC; no PR body.
- https://github.com/metaevo-ai/harness-zero/commit/0c991a4b2ee9e5ceac546f7cdd209d860e3aeeb5 — author timestamp08:24:24, committer08:28:59 UTC, October26.
- https://github.com/metaevo-ai/harness-zero/commit/8697d54462e45caaa239b0a999acacd36399435b — merge commit08:31:43 UTC, October26.

**Read scope:** complete commit patch (two files, six additions / four deletions) and PR metadata; not full repository, tests or benchmark execution. API reads: `https://api.github.com/repos/metaevo-ai/harness-zero/commits/0c991a4b2ee9e5ceac546f7cdd209d860e3aeeb5` and `https://api.github.com/repos/metaevo-ai/harness-zero/pulls/1`.

**Static reviewer interpretation:** CLI and `train_positive_sft` now pass/use `None` for unspecified checkpoint epochs. The training function filters the old default `(0.5, 1.0, 2.0, 3.0)` to points `<= epochs`; explicit user checkpoints still undergo the existing range validation. This prevents the old default list from triggering its out-of-range check when the training duration is shorter than three epochs. The patch adds neither evaluation results nor a SWE-Serve integration. It is useful implementation maintenance, not evidence closing the E2E research gap. No runtime correctness claim is made.

These queries cover commits reachable from the default branch within the stated timestamps, not all branches, separate releases, unpublished work or publication outside these repositories.

- Primary metadata: https://arxiv.org/abs/2610.31650 , retrievedOctober26 ~18:08–18:09 UTC. Submission history still lists only **v1, October22 17:57:04 UTC**. October23 announcement remains the prior discovery date. Read scope today: abstract-page version history and visible links only; **not** a new full-text read.
- A bounded release search located aggregators and existing paper listings, not a verified author implementation or substantive revision. Generic alphaXiv “replicate” tooling and arXiv code-finder toggles are **not** an author implementation. This is bounded non-discovery, not proof that no code exists.
- task-level UCR denominator; observed minimum unsafe omission cardinality and exhaustive-only no-failure sentinel for SBM; task-weighted PUR over matched nonempty masks, both twins recovering all omitted facts and subsequently acting appropriately without invalid actions; persistent true-but-incomplete observations; audit-before-terminal-commit. Single-rollout, adaptive-coverage and perfect-audit limitations apply; explanatory toys are not author replication or production-safety demonstrations.

No fresh author-linked SabreAgent/ORPR implementation, major Watch-paper correction, or validated new industrial recommendation / incrementality result was verified from this limited search. The known AMV anonymous repositories and HERD repository were not reopened without a new update signal. No new primary full text was selected from search. This finding does **not** certify that all tracked papers or repositories are unchanged.
