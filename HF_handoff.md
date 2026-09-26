# GitHub ↔ Hugging Face handoff

Shared setting: N=20, K=4, M=100, unit demand; r=100 E S, eligibility r>=60, R=1; highest eligible risk gets a free reserved slot and exits; remaining three slots use first-price payments; no eligible request means four auction slots. Scores are fixed before bidding. Lower PM ID breaks exact ties. Outside credits have fixed unit value; this is one batch.

The GitHub numerical baseline b=0.8v is **assumed**, not the multi-slot equilibrium or observed human behavior. The single-slot b=(n-1)v/n benchmark applies only in its separately specified symmetric independent uniform, risk-neutral setting. If HF uses that single-slot exercise, explicitly distinguish it from the 20-PM four-slot mechanism; do not tell participants 0.8v is the correct equilibrium strategy.

Recommended minimum viable HF artifact (Zhenning's part):

1. Display a clear decision setting and a worked payoff example. In the main batch, total wealth is x*v+100-p, net utility is x*v-p, and losers pay zero.
2. Present gain/loss framing versions with identical numerical values, information, feasible bids and final payoffs. Do not change payment rules while calling it a pure framing comparison.
3. Structure anonymous reflection/peer-play records: participant code, condition, synthetic case ID, value, exposure, severity, public risk, eligibility, reserve outcome, bid, allocation, payment, utility, comprehension check, reason for bid, and order of exposure. Keep identifying information out of public results.
4. Record only actual responses. Small convenience samples support exploratory descriptions, not population causal estimates. State alternative explanations: misunderstanding, risk attitudes, beliefs and order/learning effects.
5. Compare the observed bid ranking/distribution with the stylized GitHub assumption; a meaningful ranking change should trigger a rerun using a documented data import rather than a claim that all common bid increases change allocation. **Human-data import remains planned** in this repository.

Cross-artifact validation: verify the same case gives the same eligibility, winners, payment and utility in HF and GitHub. The deterministic demo is `demo_inputs.csv`, with expected 60 PM-mechanism rows in `reference_outputs.zip` → `results/demo_allocations.csv`. A separate hand-check case in the tests has (v,r)=(100,10),(90,20),(80,30),(70,40),(10,90): pure chooses IDs 1–4, hybrid 5/1/2/3; payments 80/72/64/56 versus 0/80/72/64; at lambda=1 hybrid W is 10 lower.

Both authors should inspect and endorse Sections 1–5. Before submission add the actual HF URL and version, peer-play limitations, and the consequential retain/qualify/revise decision in Section 4. GitHub execution does not establish that the HF artifact works.
