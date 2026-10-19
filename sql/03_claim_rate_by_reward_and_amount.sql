-- Q3. Claim rate by reward type and amount band.
-- Business question: do recipients claim some reward types and
-- some denominations more reliably than others?

SELECT
    reward_type,
    CASE
        WHEN amount_usd < 10  THEN 'Under $10'
        WHEN amount_usd < 25  THEN '$10 to $24'
        WHEN amount_usd < 100 THEN '$25 to $99'
        WHEN amount_usd < 250 THEN '$100 to $249'
        ELSE '$250 and up'
    END                                                 AS amount_band,
    COUNT(*)                                            AS delivered,
    SUM(CASE WHEN status = 'claimed' THEN 1 ELSE 0 END) AS claimed,
    ROUND(100.0 * SUM(CASE WHEN status = 'claimed' THEN 1 ELSE 0 END)
          / COUNT(*), 1)                                AS claim_rate_pct
FROM payouts
WHERE delivered_at <> ''
GROUP BY reward_type, amount_band
ORDER BY reward_type, MIN(amount_usd);
