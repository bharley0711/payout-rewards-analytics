-- Q4. Sender leaderboard with window functions.
-- Business question: which senders drive volume, and how does each
-- sender's claim rate compare with the platform average?

WITH sender_stats AS (
    SELECT
        sender_name,
        sender_industry,
        COUNT(*)                                            AS issued,
        ROUND(SUM(amount_usd), 2)                           AS value_issued_usd,
        ROUND(100.0 * SUM(CASE WHEN status = 'claimed' THEN 1 ELSE 0 END)
              / COUNT(*), 1)                                AS claim_rate_pct
    FROM payouts
    GROUP BY sender_name, sender_industry
)
SELECT
    RANK() OVER (ORDER BY value_issued_usd DESC)            AS value_rank,
    sender_name,
    sender_industry,
    issued,
    value_issued_usd,
    claim_rate_pct,
    ROUND(claim_rate_pct - AVG(claim_rate_pct) OVER (), 1)  AS pct_pts_vs_platform_avg,
    ROUND(100.0 * value_issued_usd / SUM(value_issued_usd) OVER (), 1)
                                                            AS share_of_value_pct
FROM sender_stats
ORDER BY value_rank;
