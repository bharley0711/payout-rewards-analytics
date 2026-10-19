-- Q8. Data quality checks that run before any number is shared.
-- Every check should return 0 (or an explained, documented count)
-- before the dashboard is trusted.

SELECT 'duplicate payout_id' AS check_name,
       COUNT(*) - COUNT(DISTINCT payout_id) AS problem_rows FROM payouts
UNION ALL
SELECT 'negative or zero amount',
       COUNT(*) FROM payouts WHERE amount_usd <= 0
UNION ALL
SELECT 'claimed without delivery',
       COUNT(*) FROM payouts WHERE claimed_at <> '' AND delivered_at = ''
UNION ALL
SELECT 'claimed before issued',
       COUNT(*) FROM payouts WHERE claimed_at <> '' AND claimed_at < issued_at
UNION ALL
SELECT 'delivered before issued',
       COUNT(*) FROM payouts WHERE delivered_at <> '' AND delivered_at < issued_at
UNION ALL
SELECT 'claimed status but no claimed_at',
       COUNT(*) FROM payouts WHERE status = 'claimed' AND claimed_at = ''
UNION ALL
SELECT 'unknown status value',
       COUNT(*) FROM payouts
       WHERE status NOT IN ('claimed', 'pending_unclaimed',
                            'expired_unclaimed', 'delivery_failed');
