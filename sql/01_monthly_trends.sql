-- Q1. Monthly volume, value, and claim performance.
-- Business question: is the platform growing, and does claim
-- performance move with volume?
-- SQLite date syntax shown; strftime maps to DATE_TRUNC in
-- Postgres/Snowflake and FORMAT_DATE in BigQuery.

SELECT
    strftime('%Y-%m', issued_at)                       AS issue_month,
    COUNT(*)                                           AS payouts_issued,
    ROUND(SUM(amount_usd), 2)                          AS value_issued_usd,
    SUM(CASE WHEN delivered_at <> '' THEN 1 ELSE 0 END) AS payouts_delivered,
    SUM(CASE WHEN status = 'claimed' THEN 1 ELSE 0 END) AS payouts_claimed,
    ROUND(100.0 * SUM(CASE WHEN status = 'claimed' THEN 1 ELSE 0 END)
          / COUNT(*), 1)                               AS claim_rate_pct_of_issued,
    ROUND(AVG(CASE WHEN claimed_at <> ''
        THEN (julianday(claimed_at) - julianday(delivered_at)) * 24
        END), 1)                                       AS avg_hours_to_claim
FROM payouts
GROUP BY issue_month
ORDER BY issue_month;
