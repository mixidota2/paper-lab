# Dated primary-source notes, 2026-10-26

Historical authored findings. Source-read scope and uncertainty are preserved; no new primary review or experiment was performed for the migration.

1. **Proximal Residual (2609.23242): expand OOS, do not interpret it as out-of-stock.** Primary Section 6/Table 1 specifies shipping-plus-transfer cost per fulfilled unit: normalized State-prox 0.950 ± 0.028 versus deterministic historical proxy 1.000. All offline; capacity-price penalties excluded. Thus do not call the 5% a stockout-rate improvement. Existing v1 remains September 19. Read abstract, Sections 1–4, and targeted Sections 6–7; no proof audit or replication. Primary: https://arxiv.org/html/2609.23242v1#S6 ; history: https://arxiv.org/abs/2609.23242 . 
2. **SCQ (2610.17465): version-scope flag only.** Primary history now explicitly lists v2 October 19, 16:35:10 UTC (v1 October 12, 22:27:59 UTC). The October 20 assumption review cites v1. This pass inspected metadata/abstract only; it does **not** establish a material v2 change and does not redo the completed assumption review. Not October 23–25 evidence. https://arxiv.org/abs/2610.17465 .

## Surfaced sources and exclusion/read scope

### Springer pricing/censoring paper — out-of-window, not featured

**Causally informed multimodal offline reinforcement learning for constrained promotional pricing in omnichannel convenience retail**, Qi Liu, DOI 10.1007/s10791-026-10645-5.
https://link.springer.com/article/10.1007/s10791-026-10645-5

Publisher explicitly dates publication **October 21, 2026**. Read title/date, abstract/introduction, targeted data/predecision-timing text, Sections 5.1–5.5 and limitations/data-availability excerpts; not the complete methods, image-rendered tables, code, or underlying data. Authors combine multimodal demand, cross-fitted doubly robust adjustment, conservative offline RL, and constraints. They report estimated +8.7% contribution profit and 8.9%→8.1% stockout rate, but explicitly only observational/model-based evaluation, not field deployment. XGBoost is a pricing baseline, not a matched TSFM comparison. Severely censored observations are excluded from main causal estimation; this is not validated natural-stockout latent recovery. Private data available on request. No new-window update was identified.

### Other discovery only — no paper evaluation

- CADRE: **Demand Hidden by Stockouts: Censored Demand Recovery and Green Waste-Reduction Forecasting for Sustainable Fresh-Food Consumption Under Emerging-Market Urbanization**, https://doi.org/10.3390/su18157642 . Search result labeled publication three months ago and exposed methodological excerpts (joint censored likelihood/newsvendor training, artificial recensoring). DOI open returned **429 Too Many Requests**. Full text not acquired/read; no assessment from snippets. Not new-window evidence.
- **Stockout-Aware Relational Demand Forecasting and Cross-Dataset Error Trade-offs**, https://jtie.stekom.ac.id/index.php/jtie/article/view/594 , DOI 10.51903/jtie.v4i1.594. Primary search-result abstract only; result date labeled 1.5 years ago, unverified. Abstract itself distinguishes artificial masking recovery from natural-stockout truth and reports accuracy rather than inventory service. No full-text judgment or registry addition.
- **Diffusion-aware Censored Gaussian Processes for Demand Modelling**, https://ijcai.org/proceedings/2025/857 , DOI 10.24963/ijcai.2025/857. Primary proceedings abstract only, clearly 2025. Not a new result; no full read or recommendation.
- 2610.31153 **Balanced Posted Prices in Stationary Two-Sided Markets**, arXiv primary listing abstract only, submitted October 22. Theory for limited-storage intermediaries; not retail TSFM/recovery/service evidence.

## Addendum — independent Hayashida appendix review

Source: https://www.kohei-hayashida.com/files/papers/demand_estimation_pricing_perishable_food_appendix.pdf . Title **Demand estimation and pricing of perishable food**, Kohei Hayashida, June 4, 2026. Author-hosted 20-page PDF. All Section C/D extracted text and endnotes read (printed pages 11–20), with earlier sample-construction context. Numerical reading is from parsed primary text, not independent visual verification. No code/data/replication package inspected or run.

- The +6.32% field estimate is a single-store before/after profit ratio adjusted by same-store non-fried-food revenue, **not** randomized stores. Fried-product DiD controls are contaminated by shared-labor reallocation.
- Production changed alongside markdown removal. Hence the field gain is not the isolated causal effect of removing discounts; +2.24pp is a fixed-supply structural prediction, and +4.08pp residual has a qualitative freshness/production interpretation rather than independent causal decomposition.
- C's timing and conditional-purchase diagnostics support, but do not prove, exogenous arrivals or the inside-only choice specification. D's endnote explicitly leaves some context-specific signaling unidentified without exogenous exposure/control-store variation.
