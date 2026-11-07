# Dated primary-source notes, 2026-10-26

Historical authored findings. Source-read scope and uncertainty are preserved; no new primary review or experiment was performed for the migration.

## EpiSEM-Bench — evaluation design

**Title:** EpiSEM-Bench: Evaluating Safety and Evidence Recovery in LLM Agents under Missing Evidence. **Authors:** Qijin Zhang, Hanzhen Wang, Yuehan Zhao, Haoyu Dai, Yao Shu, Zhongxiang Dai, Shuang Qiu. **v1 submitted:** 2026-10-22 17:57:04 UTC; **announced:** October23. **Sources:** https://arxiv.org/abs/2610.31650 ; https://arxiv.org/html/2610.31650v1 .

**Read scope:** complete main text, definitions/equations 1–2, all evaluation tables, Appendix B boundary algorithm, C coverage/matched comparisons, D recovery/failure/cost, E provenance; selected Appendix A examples. HTML text/tables, not a visual figure audit. No original code or rollout artifact inspected; not an independent replication. No public author-code link located in the paper or bounded exact-title search.

**Author report:** 300 safe/unsafe task pairs across six domains; true observations can omit decisive facts. Persistent atom suppression and optional perfect audit recovery separate action success from evidence-supported success. GPT-6-Luna has SBM 84.8% but PUR 30.5%; DeepSeek-V4.1-Flash has SBM 68.4% and PUR 58.4% (Table 1).

**Review:** this advances the remember/re-fetch question beyond verifier brittleness: facts can be true yet insufficient, and restored evidence must support both restraint and legitimate completion. Main limitation: one temperature-zero rollout/condition, model-dependent adaptive mask coverage, synthetic rules and perfect all-facts recovery. Do not treat rankings or observed boundaries as stable safety guarantees.

**Context:** TRACE tests evaluator brittleness; EpiSEM asks whether an agent recognizes a missing premise and uses recovered evidence before acting. Related-work reading pointers in the primary: AgentAbstain (matched act/abstain tasks), AgentNoiseBench, AgentDojo, ToolSandbox; EpiSEM §2 distinguishes its persistent fact-level omission and paired recovery.

**Paper metric definitions:**

- `UCR = number of tasks with any prohibited commit / N`; not failures/rollouts.
- `SBM = (1/N) Σ_i m_i/(c_i+1)`. `c_i`: critical atoms; `m_i`: smallest **observed** unsafe omission cardinality; baseline failure gives0; exhaustive no-failure sentinel is`c_i+1`.
- `PUR = (1/N) Σ_i (1/q_i) Σ_j p_ij`. `p_ij=1` only when **both** matched recovery twins restore all omitted atoms, then unsafe twin abstains/escalates and safe twin legally completes; no invalid action. `q_i`: matched nonempty masks.
- Boundary search: baseline → all required singleton controls → increasing-cardinality masks until unsafe witness/exhaustion. Never assume omission risk monotonicity. Compare SE/RE only on aligned masks.

## AMV-Guard — qualified review

**Title:** When Is a Memory Safe Enough to Act On? Action-Conditioned Verification for Long-Lived Agents. **ID:**2610.31446. **v1:**2026-10-22 15:43:50 UTC; announced October23. **Sources:** https://arxiv.org/abs/2610.31446 ; https://arxiv.org/html/2610.31446v1 .

Read main formulation/method/evaluation/limitations, selected calibration/OOD/uncertainty/protocol/algorithm/reproducibility appendices; not complete proof audit or code read. Author-linked anonymous repositories exist, but were not opened: https://anonymous.4open.science/r/AMV-Guard-AEF6/ ; https://anonymous.4open.science/r/AMV-Guard-3668/ ; https://anonymous.4open.science/r/AMV-Guard-AB3A/ .

Author report: ToolSandbox verification cost 1.843→1.219 versus static AMV, with zero gate harm but 7.03% raw end-to-end harm. AppWorld transfers only the stopping core: cost 2.655→2.090, task success 30.5%→28.0%. Review: action-conditioned re-verification is useful; information matters only if it can change the terminal decision. However extractor omissions, approximate joint dependencies/binary verifier observations, and incomplete artifact release limit the claim. Gate-local success cannot be promoted to E2E safety.

## HERD — qualified review

**Title:** HERD: Harness-Evolving Recursive Distillation for Continual Learning. **ID:**2610.31401. **v1:**2026-10-22 15:03:20 UTC; announced October23. **Sources:** https://arxiv.org/abs/2610.31401 ; https://arxiv.org/html/2610.31401v1 . Author repository linked: https://github.com/a1exsun/HERD (not inspected).

Read introduction, method, main experiments/ablation, seed accounting, failure cases and future-work scope. This is a focused primary read, not complete supplementary audit. Author report: Qwen3.5-4B on 25 supervised tasks, three seeds; dual previous/base anchors reduce forgetting and general-capability loss while internalizing skills. Review: verified answers and known task boundaries are required; ablations single-seed. Probe coverage/length and output-format retention account for important boundaries. It does not establish runtime agent memory or SWE-Serve correctness. **TRACE+17 is the older continual-learning benchmark, not verifier-brittleness TRACE 2610.11678.**

## Abstract-only / discovery-only, not evaluated

- **2610.31314, When LLMs Forget What They Believe: Characterizing State Integrity Collapse in Long-Horizon Dialogues.** v1 October22 14:08:48 UTC, Oct23 cs.CL announcement. https://arxiv.org/abs/2610.31314 . Abstract/history only; potentially useful recall/compliance separation, but no full-text assessment.
- REGATTA2610.30924, OPTICYCLE/OPTISTATE2610.30917, HiSTEVE2610.31162, BGAFlow2610.30825: search-result abstracts only; no primary full-text assessment or selection.
