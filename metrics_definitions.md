# Metrics definitions

One definition per metric, used by every query in `sql/`, the Tableau
workbook, and the README. If a number cannot be traced to a definition
here, it does not get shared. This file is the semantic layer for the
project.

Snapshot date for all "as of" logic: **2026-06-30 23:59:59**.

| Metric | Definition | Grain | Notes |
| --- | --- | --- | --- |
| Payouts issued | Count of rows in `payouts` | Per period or segment | One row is one payout. |
| Value issued (USD) | `SUM(amount_usd)` | Per period or segment | Face value at issue, not at claim. |
| Delivery rate | Delivered payouts / issued payouts | Per segment | Delivered means `delivered_at` is not empty. |
| Claim rate (of issued) | Claimed payouts / issued payouts | Per segment | Denominator includes delivery failures. Use for platform health. |
| Claim rate (of delivered) | Claimed payouts / delivered payouts | Per segment | Denominator excludes delivery failures. Use for recipient behavior. Never mix the two claim rates in one chart without labels. |
| Avg hours to claim | Mean of (`claimed_at` minus `delivered_at`) in hours, claimed payouts only | Per segment | Mean, not median. Long tails pull it up; say so when presenting. |
| Claimed within N days | Delivered payouts with a claim timestamp within N days of delivery / delivered payouts | Per issue-month cohort | Cohorts near the snapshot date are incomplete: their windows have not elapsed. |
| Eventual claim rate (reminder analysis) | Among payouts delivered and still unclaimed at 72 hours, the share claimed by the snapshot date | Reminder sent vs not | Association only. Reminders were not randomized. |
| Delivery failure rate | Payouts with empty `delivered_at` / issued payouts | Per sender per month | Alert threshold used in the README recommendation: 10%. |
| Share of value | Segment value issued / total value issued | Per sender | Window function in `sql/04_sender_leaderboard.sql`. |

## Status values

| Status | Meaning |
| --- | --- |
| `claimed` | Delivered and claimed by the snapshot date. |
| `pending_unclaimed` | Delivered, unclaimed, and issued less than 90 days before the snapshot date. May still claim or expire. |
| `expired_unclaimed` | Delivered, unclaimed, and issued 90 or more days before the snapshot date. Treated as final. |
| `delivery_failed` | No delivery timestamp. The recipient never had a chance to claim. |
