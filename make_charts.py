"""Build the dashboard preview image from the SQL outputs.

The same four views are specified for Tableau in
tableau/tableau_workbook_spec.md. This PNG is the static preview
embedded in the README.

Run:  python3 make_charts.py   (after run_analysis.py)
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

monthly = pd.read_csv("outputs/01_monthly_trends.csv")
funnel = pd.read_csv("outputs/02_funnel_by_campaign.csv")
reward = pd.read_csv("outputs/03_claim_rate_by_reward_and_amount.csv")
cohort = pd.read_csv("outputs/05_cohort_claim_windows.csv")

reward_overall = (
    reward.groupby("reward_type")
    .apply(lambda g: 100.0 * g["claimed"].sum() / g["delivered"].sum())
    .sort_values()
)

fig, axes = plt.subplots(2, 2, figsize=(13, 8))
fig.suptitle(
    "Payout Performance Dashboard, Jan to Jun 2026 (synthetic data)",
    fontsize=14, fontweight="bold",
)

ax = axes[0, 0]
ax.bar(monthly["issue_month"], monthly["value_issued_usd"] / 1000, color="#4C78A8")
ax.set_title("Value issued by month ($ thousands)")
ax.set_ylabel("$ thousands")
for x, y in zip(monthly["issue_month"], monthly["value_issued_usd"] / 1000):
    ax.annotate(f"{y:.0f}", (x, y), ha="center", va="bottom", fontsize=8)

ax = axes[0, 1]
ax.barh(reward_overall.index, reward_overall.values, color="#54A24B")
ax.set_title("Claim rate by reward type (% of delivered)")
ax.set_xlabel("% claimed")
for y, x in enumerate(reward_overall.values):
    ax.annotate(f"{x:.1f}%", (x, y), va="center", fontsize=9)

ax = axes[1, 0]
x = range(len(funnel))
ax.bar([i - 0.2 for i in x], funnel["delivery_rate_pct"], width=0.4,
       label="Delivery rate %", color="#4C78A8")
ax.bar([i + 0.2 for i in x], funnel["claim_rate_pct_of_delivered"], width=0.4,
       label="Claim rate % of delivered", color="#E45756")
ax.set_xticks(list(x))
ax.set_xticklabels([c.replace(" ", "\n") for c in funnel["campaign_type"]], fontsize=7)
ax.set_title("Funnel by campaign type")
ax.legend(fontsize=8)

ax = axes[1, 1]
ax.plot(cohort["cohort_month"], cohort["claimed_within_7d_pct"],
        marker="o", label="Claimed within 7 days")
ax.plot(cohort["cohort_month"], cohort["claimed_within_30d_pct"],
        marker="o", label="Claimed within 30 days")
ax.plot(cohort["cohort_month"], cohort["claimed_within_90d_pct"],
        marker="o", label="Claimed within 90 days")
ax.set_title("Cohort claim windows (% of delivered)")
ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig("images/dashboard_preview.png", dpi=150)
print("Wrote images/dashboard_preview.png")
