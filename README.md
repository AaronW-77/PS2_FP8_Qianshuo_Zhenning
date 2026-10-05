# FP8 · Session D · PS2 Computational Artifact

**Qianshuo (Aaron) Wang and Zhenning Wang — COMSCI/ECON 206, Professor Luyao Zhang**

**Can an auction with reserved capacity for objectively high-risk research requests improve the allocation of scarce AI research capacity relative to a pure auction?**

This repository implements **Section 3**, using the one-batch model in Section 2. All values and risk inputs are synthetic. It is a mechanism comparison under specified bids, not a computation of Bayesian Nash equilibrium and not evidence about actual investment returns. Sections 1–5 are joint work. Qianshuo (Aaron) Wang and Zhenning Wang jointly developed the research question, mechanism comparison, welfare framework, and linked artifacts. Individual intellectual decisions, outputs, verification steps, and responsibilities are documented in the final PS2 Author Notes.

## Final release and canonical repository

Canonical course repository:
https://github.com/dku-comsci-econ206-Autumn2026/PS2_Qianshuo_Zhenning

Notebook: 
[https://github.com/dku-comsci-econ206-Autumn2026/PS2_Qianshuo_Zhenning/blob/main/PS2_Code.ipynb](https://colab.research.google.com/drive/1I-J52wxGaAIwJK_LjtghBnXS2GxY0U2V#scrollTo=QI1TUTULTNPj)

Hugging Face Space:
https://huggingface.co/spaces/dku-comsci-econ206-2026/PS2_Qianshuo_Zhenning

A0 Poster:
https://canva.link/vlx5ljli23z7qk8

Final tested commit:
`[FINAL SHA]`



## Run and verify

Python 3.9+; no third-party packages for the simulation or tests. The recorded fresh run used Python 3.9.6 on September 26, 2026.

```sh
python3 -m unittest -v test_simulation.py
python3 simulation.py --seed 20260926 --batches 1000 --out results
python3 verify_reproduction.py
```

The last command runs the six mechanism tests, regenerates the outputs in a temporary directory, and compares every CSV cell against the actual reference run (numeric tolerance 1e-10). It also checks the reference source fingerprint. `results/` is created by the run. `reference_outputs.zip` contains the five complete reference CSVs and `fresh_run.json`; `primary_summary.csv`, `demo_inputs.csv`, and `fresh_run.json` are also provided separately for easy inspection. The demo is batch 1, selected in advance, not a favorable batch.

**Notebook:** The current runnable Colab notebook is:
https://colab.research.google.com/drive/1I-J52wxGaAIwJK_LjtghBnXS2GxY0U2V#scrollTo=QI1TUTULTNPj

An archived copy of the notebook is stored in the repository as:
`PS2_Code.ipynb`

After the final merge, the canonical GitHub notebook path is:
https://github.com/dku-comsci-econ206-Autumn2026/PS2_Qianshuo_Zhenning/blob/main/PS2_Code.ipynb

The organization-owned repository, rather than a personal fork, is the canonical final source.

## Parameters and interpretation

| Parameter | Primary setting | Reason / scope |
|---|---|---|
| PMs, slots, unit demand | N=20, K=4, at most one per PM | User's one-shot setting |
| Credits | M=100 each | One unused credit has one unit of fixed outside value |
| Private research value | v independently uniform on [0,100] | Synthetic, budget nonbinding for baseline bids |
| Exposure E and severity S | Independent uniform [0,1], independent of v | Synthetic normalized inputs, not calibrated financial quantities |
| Risk score | r=100 E S | Public, audited and frozen before reserve allocation and bidding |
| Eligibility | r >= 60 | Illustrative policy threshold, not an estimated optimal threshold |
| Reserve size | R=1 | Highest-risk eligible PM gets a free slot and exits |
| Auction bids | b=0.8v | Stylized monotone shading, held fixed across mechanisms; not multi-slot BNE |
| Arrival | Random exogenous permutation | Same order for matched FCFS comparisons |
| Welfare weight | lambda=1 | Normative index W=V+lambda C; sensitivity 0, 0.5, 1, 2 |
| Repetitions | 1,000 independently generated batches | Monte Carlo replications, **not sequential rounds played by the same PMs** |
| Seed | 20260926 | Fixed before inspection; no seed search |
| Tie rule | Lower PM ID | Public deterministic rule, no bid-dependent risk tie-breaking |

Full payoff is x*v+(100-p). Subtracting the fixed 100 yields u=x*v-p. Outside opportunities introduce no strategic stage here. Each batch terminates after a single sealed-bid allocation and payment, with no feedback, carryover, learning or subsequent strategic choice. The 1,000 replications therefore do not turn the model into a dynamic game.

## Language-independent algorithm

```text
FOR each synthetic batch:
    draw 20 private values, frozen exposure/severity scores, and an arrival order
    fix assumed bids (same PM bid under each mechanism)
    PURE: award four slots to highest bids; each winner pays own bid
    HYBRID:
        rank eligible requests (r >= threshold) by descending risk
        award up to R reserved slots at zero payment; remove their recipients
        return any unused reserved slots to the auction
        award remaining capacity to highest remaining bids; pay own bid
    FCFS: award four slots by exogenous arrival order; no payment
    resolve ties by lower PM ID; stop after the batch; no PM receives two slots
    record winner IDs, payments, utilities, V, C, W, efficiency, eligible access
COMPARE paired hybrid-minus-pure outcomes; average across independent batches
REPEAT for predeclared threshold, reserve, value–risk alignment and bid scenarios
```

The auction mapping is four indivisible premium AI research slots, 20 unit-demand PMs, private values, verified public risk, one simultaneous sealed bid, a deterministic allocation, and internal-credit first-price payments. Desired improvement is a transparent trade-off between private value and risk coverage. The application boundary is important: verified risk is not a report whose truthfulness is established by the mechanism; risk coverage is not avoided loss; correlated/common financial values, strategic portfolio choice, endogenous arrival, resale, complementarities and future rounds are excluded.

## Metrics and actual fresh-run results

V=sum of allocated private values; C=sum of their risk scores; W=V+lambda*C. Total PM utility is V minus total payments. Payments are transfers inside the firm, so are not subtracted again from W. Private-value efficiency is V divided by the sum of the top four values. Eligible access is the fraction of eligible requests served, averaged only over batches with at least one eligible request (blank/NA otherwise).

Mean per batch, primary settings:

| Mechanism | V | C | W (lambda=1) | Payments | Total PM utility |
|---|---:|---:|---:|---:|---:|
| Pure first-price | 353.08 | 101.35 | 454.43 | 282.46 | 70.62 |
| Hybrid, R=1 | 326.26 | 137.95 | 464.20 | 226.98 | 99.28 |
| FCFS | 199.45 | 100.43 | 299.88 | 0.00 | 199.45 |

Hybrid sacrifices 26.82 private-value units and adds 36.59 risk-score units. Mean W rises 9.78 at lambda=1 (paired Monte Carlo SE 0.89), but falls 8.52 at lambda=0.5. The ratio of mean value loss to mean coverage gain is 0.733; this is the break-even weight for **mean** W in this sample, not the mean of individual batch thresholds. Hybrid strictly improves W in 43.8% of all batches at lambda=1, so a positive average must not be called universal dominance. Its private-value efficiency averages 92.42% versus 100% for the pure auction under the common monotone bid rule; eligible access averages 66.70% versus 20.29%.

The code evaluates 36 scenarios: thresholds {40,60,80}, R in {1,2}, three alignments, and two bidding rules. The alignment stress tests keep the same value multiset and risk scores but sort values with risk or against risk. These are deliberately extreme dependence tests, not independent-value models. Heterogeneous shading draws an independent factor uniform on [0.5,1] for each PM and holds it fixed across mechanisms. These draws model hypothetical behavior, not observed peer behavior. The primary rule ignores changes in equilibrium bidding induced by the reserve, which is a substantive limitation.

At threshold 60 and R=1, common shading gives mean hybrid-minus-pure W of 0 under perfect positive rank alignment and -3.24 under negative rank alignment (lambda=1). With heterogeneous shading these become +10.75 and -2.34; the independent case is +13.12. Thus the project decision is conditional: do not recommend a reserve from eligibility alone; establish the firm's welfare weight and value–risk relationship, then test sensitivity to actual bids. Changing a *common* shading coefficient alone cannot change allocation rankings in this unconstrained setting.

Monte Carlo SE describes simulation sampling uncertainty, not empirical confidence about financial performance or classroom behavior. BNE remains an economic benchmark; the simulation does not solve it. Risk scores are observable within the modeled batch; values and latent shading factors are not made public by the simulation assumption.

## Files, verification, and evidence status

- `simulation.py`: synthetic generator, allocation rules, metrics and 36 scenarios.
- `test_simulation.py`: six tests covering fallback, known displacement/payments, reserve already an auction winner, score/bid ties and threshold equality, budget cap/duplicate rejection, and paired allocation/accounting invariants.
- `PS2_comparison.ipynb`: independently runnable, executed notebook.
- `reference_outputs.zip`: actual outputs, including winner IDs for every primary batch and all 60 PM-mechanism outcomes for the demo.
- `fresh_run.json`: seed, parameters, Python version, source SHA-256, output SHA-256 fingerprints.
- `verify_reproduction.py` and `verification.txt`: clean rerun comparison and its actual record.
- `HF_handoff.md`: shared schema and behavioral interface; no fabricated participant responses.

Completed: synthetic comparison, six tests, clean rerun, executed notebook, Hugging Face behavioral interface, A0 poster integration, and symposium peer review.

## AI use and license

OpenAI ChatGPT and Codex assisted with model clarification, code and notebook review, debugging, reproducibility checks, literature checking, and language editing. The authors independently reviewed the final assumptions, parameter choices, outputs, interpretations, and limitations and remain responsible for all claims and results.

No human behavioral outcomes were fabricated or inferred. Completed computational evidence, exploratory behavioral evidence, and planned future work are labeled separately.

This repository includes an MIT License for the authors' original code and project files where applicable. External software and referenced sources remain under their own licenses and terms.
