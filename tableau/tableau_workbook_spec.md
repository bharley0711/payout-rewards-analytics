# Tableau workbook spec

This file specifies the Tableau workbook that pairs with this project,
sheet by sheet, so it can be rebuilt exactly in Tableau Desktop or
Tableau Public. The data source is `data/payouts.csv`. Field
definitions come from `metrics_definitions.md`; nothing here uses a
metric that is not defined there.

A static preview of the same four views is in
`images/dashboard_preview.png`.

## Data prep (Tableau Prep or Desktop)

- Connect to `data/payouts.csv` as a single table extract.
- `issued_at`, `delivered_at`, `claimed_at`: convert to datetime.
  Empty strings in the CSV import as nulls, which is what we want.
- `amount_usd`: measure, currency USD.
- Create calculated fields:
  - `Is Delivered`: `NOT ISNULL([delivered_at])`
  - `Is Claimed`: `[status] = "claimed"`
  - `Hours to Claim`: `DATEDIFF('hour', [delivered_at], [claimed_at])`
  - `Amount Band`: the CASE logic from
    `sql/03_claim_rate_by_reward_and_amount.sql`
  - `Issue Month`: `DATETRUNC('month', [issued_at])`

## Sheet 1: Monthly volume and value

- Columns: `Issue Month`. Rows: `SUM(amount_usd)`.
- Bar chart, label values in dollars.
- Filter: none. This is the context view for the whole dashboard.

## Sheet 2: Claim rate by reward type

- Rows: `reward_type`. Columns: claim rate of delivered,
  `SUM([Is Claimed]) / SUM([Is Delivered])`, formatted as percent.
- Sort descending. Reference line at the platform average.

## Sheet 3: Funnel by campaign type

- Rows: `campaign_type`. Two bar measures side by side:
  delivery rate and claim rate of delivered (definitions in
  `metrics_definitions.md`).
- Sort by claim rate of delivered, descending.

## Sheet 4: Cohort claim windows

- Columns: `Issue Month`. Rows: three lines, percent of delivered
  claimed within 7, 30, and 90 days of delivery.
- Calculated fields use `DATEDIFF('day', [delivered_at], [claimed_at])`.
- Annotate the most recent month as an incomplete cohort. Its windows
  have not fully elapsed at the snapshot date, so it reads low.

## Dashboard

- 2 by 2 grid of Sheets 1 to 4, title:
  "Payout Performance, Jan to Jun 2026".
- Global filters: `sender_name`, `campaign_type`, `reward_type`.
- Every number on the dashboard must trace to a definition in
  `metrics_definitions.md` and a query in `sql/`.
