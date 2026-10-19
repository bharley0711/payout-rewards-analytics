-- Q5. Cohort claim windows by issue month.
-- Business question: how quickly do recipients act? What share of
-- eventual claims land inside 7, 30, and 90 days of delivery?

SELECT
    strftime('%Y-%m', issued_at)                        AS cohort_month,
    SUM(CASE WHEN delivered_at <> '' THEN 1 ELSE 0 END) AS delivered,
    ROUND(100.0 * SUM(CASE WHEN claimed_at <> ''
        AND julianday(claimed_at) - julianday(delivered_at) <= 7
        THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN delivered_at <> '' THEN 1 ELSE 0 END), 0), 1)
                                                        AS claimed_within_7d_pct,
    ROUND(100.0 * SUM(CASE WHEN claimed_at <> ''
        AND julianday(claimed_at) - julianday(delivered_at) <= 30
        THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN delivered_at <> '' THEN 1 ELSE 0 END), 0), 1)
                                                        AS claimed_within_30d_pct,
    ROUND(100.0 * SUM(CASE WHEN claimed_at <> ''
        AND julianday(claimed_at) - julianday(delivered_at) <= 90
        THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN delivered_at <> '' THEN 1 ELSE 0 END), 0), 1)
                                                        AS claimed_within_90d_pct
FROM payouts
GROUP BY cohort_month
ORDER BY cohort_month;
