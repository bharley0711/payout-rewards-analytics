-- Q2. Funnel by campaign type: issued -> delivered -> claimed.
-- Business question: where does each use case lose recipients,
-- at delivery or at claim?

SELECT
    campaign_type,
    COUNT(*)                                            AS issued,
    SUM(CASE WHEN delivered_at <> '' THEN 1 ELSE 0 END) AS delivered,
    SUM(CASE WHEN status = 'claimed' THEN 1 ELSE 0 END) AS claimed,
    ROUND(100.0 * SUM(CASE WHEN delivered_at <> '' THEN 1 ELSE 0 END)
          / COUNT(*), 1)                                AS delivery_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN status = 'claimed' THEN 1 ELSE 0 END)
          / NULLIF(SUM(CASE WHEN delivered_at <> '' THEN 1 ELSE 0 END), 0), 1)
                                                        AS claim_rate_pct_of_delivered,
    ROUND(AVG(CASE WHEN claimed_at <> ''
        THEN (julianday(claimed_at) - julianday(delivered_at)) * 24
        END), 1)                                        AS avg_hours_to_claim
FROM payouts
GROUP BY campaign_type
ORDER BY claim_rate_pct_of_delivered DESC;
