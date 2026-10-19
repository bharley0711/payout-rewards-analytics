-- Q7. Delivery health by sender and month.
-- Business question: is any sender quietly losing payouts at the
-- delivery step? This is the query that surfaces the March 2026
-- incident for the largest sender.

SELECT
    sender_name,
    strftime('%Y-%m', issued_at)                        AS issue_month,
    COUNT(*)                                            AS issued,
    SUM(CASE WHEN delivered_at = '' THEN 1 ELSE 0 END)  AS delivery_failures,
    ROUND(100.0 * SUM(CASE WHEN delivered_at = '' THEN 1 ELSE 0 END)
          / COUNT(*), 1)                                AS failure_rate_pct
FROM payouts
GROUP BY sender_name, issue_month
HAVING COUNT(*) >= 50
ORDER BY failure_rate_pct DESC
LIMIT 10;
