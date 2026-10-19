-- Q6. Reminder effect, measured honestly.
-- Population: payouts still unclaimed 72 hours after delivery.
-- Half the battle in analysis is the denominator: comparing claim
-- rates only inside this at-risk group keeps the comparison fair.
-- Note: reminders were not randomized in this simulated data, so
-- this is an association, not a causal estimate.

SELECT
    reminder_sent,
    COUNT(*)                                            AS unclaimed_at_72h,
    SUM(CASE WHEN status = 'claimed' THEN 1 ELSE 0 END) AS eventually_claimed,
    ROUND(100.0 * SUM(CASE WHEN status = 'claimed' THEN 1 ELSE 0 END)
          / COUNT(*), 1)                                AS eventual_claim_rate_pct
FROM payouts
WHERE delivered_at <> ''
  AND (claimed_at = '' OR julianday(claimed_at) - julianday(delivered_at) > 3)
  AND julianday('2026-06-30 23:59:59') - julianday(delivered_at) >= 3
GROUP BY reminder_sent
ORDER BY reminder_sent DESC;
