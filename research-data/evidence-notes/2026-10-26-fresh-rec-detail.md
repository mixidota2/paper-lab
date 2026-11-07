# Dated primary-source notes, 2026-10-26

Historical authored findings. Source-read scope and uncertainty are preserved; no new primary review or experiment was performed for the migration.

## PAIR — Watch, qualified review

- ID/title: 2610.30941, *PAIR: Preference-Aligned Intent Retrieval for Premium People Recommendation at LinkedIn*.
- Submitted: 2026-10-22 08:57:58 UTC; announced October23.
- Sources: https://arxiv.org/abs/2610.30941 and https://arxiv.org/html/2610.30941v1 ; https://arxiv.org/pdf/2610.30941v1 .
- Read scope: abstract/history; main methods, tables 1–4, evaluation and limitations. PDF page 7 (zero-based page 6) text confirms metric wording and table; not merely an HTML-conversion anomaly. No code/replication.
- Author report: retrieval-embedding replacement within a fixed ranker; CTR +7.5%, Premium retention +2.1%. Dominant gain is task-specific supervision, not history architecture.
- Review: §5.1 calls evaluation a fixed 100-candidate pool, yet MAR@100<1; definition needs clarification, not an accusation of invalid data. Online sample size, dates, confidence intervals are absent. Exposure bias acknowledged; not causal-uplift optimization. Preserve as Watch rather than map-changing evidence.

## OneLatent — Watch, qualified review

- ID/title: 2610.30675, *OneLatent: Latent Reasoning for Efficient Foundation Recommendation Models*.
- Submitted: 2026-10-22 03:39:38 UTC; announced October23.
- Sources: https://arxiv.org/abs/2610.30675 and https://arxiv.org/html/2610.30675v1 .
- Read scope: main methods/results and Appendix A implementation/data construction; not all prompts or figure pixels. No code/replication.
- Author report: latent-token training plus asynchronous, behavior-triggered cached retrieval channel; incumbent cascade retained.
- Review: 17.49× throughput compares against explicit CoT, not No-Think (essentially equal). Industrial strongest-baseline gains are 1.58% SID@64 / 0.45% ID@64. Seven-day 5%-per-arm online test reports impressions +2.566%, ad spend +5.157%; revenue +9.6% is a posterior estimate. Model and serving changes are bundled. No strict latent bottleneck; one seed. Useful qualification, insufficient new map cell.

## LARA — Watch, not validated incrementality

- ID/title: 2610.30423, *When Agentic Retrieval Fails Silently: Framework and Production Evidence from a Creative AI Assistant*.
- Submitted: 2026-10-21 20:32:56 UTC; announced October23.
- Sources: https://arxiv.org/abs/2610.30423 and https://arxiv.org/html/2610.30423v1 .
- Read scope: entire main HTML, including framework, production evidence, limitations; no raw telemetry.
- Author proposal: separate retrieval, consumption/use, and downstream outcome measurements with lineage; distinguish absent retrieval from poor ranking.
- Review: useful instrumentation boundary, but none of four lineage fields implemented; proposed relevance/attribution metrics not computed; telemetry schema validation absent. Observational Adobe Express proxies motivate the proposal rather than validate it. No causal incremental-value finding or measured repair.
