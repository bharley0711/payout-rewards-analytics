"""Generate a fully synthetic payout and rewards dataset.

Simulates six months (Jan-Jun 2026) of payouts sent through a fictional
rewards platform: companies issue payouts, recipients receive a delivery
(email), and most recipients claim the reward. Every company name,
recipient, and transaction is invented. No real data is used.

Planted, discoverable patterns (so the SQL analysis has something real
to find):
1. A reminder email at 72 hours materially lifts claim rates.
2. Claim rate rises with payout amount; small payouts are often ignored.
3. One large sender has a delivery failure spike in March 2026.
4. Bank transfer (ACH) claims best; charity donations claim worst
   (many donors never complete the flow).
5. Research incentives are claimed fastest; employee recognition slowest.

Run:  python3 generate_data.py
Writes: data/payouts.csv
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)

SENDERS = [
    ("SND-001", "Northwind Traders", "Retail"),
    ("SND-002", "Acme Logistics", "Logistics"),
    ("SND-003", "Bluepeak Software", "Technology"),
    ("SND-004", "Harborview Health", "Healthcare"),
    ("SND-005", "Summit Financial Group", "Finance"),
    ("SND-006", "Brightpath Education", "Education"),
    ("SND-007", "Cascade Manufacturing", "Manufacturing"),
    ("SND-008", "Lumen Energy", "Energy"),
    ("SND-009", "Foxglove Media", "Media"),
    ("SND-010", "Atlas Insurance", "Insurance"),
    ("SND-011", "Juniper Retail Group", "Retail"),
    ("SND-012", "Meridian Travel", "Hospitality"),
]

CAMPAIGNS = [
    "Employee recognition",
    "Customer rebate",
    "Research incentive",
    "Sales SPIF",
    "Referral bonus",
    "Survey incentive",
]

REWARD_TYPES = ["Gift card", "Prepaid card", "ACH transfer", "Charity donation"]

# Base claim probability by reward type (pattern 4)
CLAIM_BASE = {
    "ACH transfer": 0.93,
    "Prepaid card": 0.88,
    "Gift card": 0.82,
    "Charity donation": 0.61,
}

# Typical amounts by campaign type
AMOUNTS = {
    "Employee recognition": [10, 25, 25, 50, 50, 100],
    "Customer rebate": [10, 15, 20, 25, 50],
    "Research incentive": [25, 50, 75, 100, 150],
    "Sales SPIF": [50, 100, 100, 250, 500],
    "Referral bonus": [25, 50, 50, 100],
    "Survey incentive": [5, 5, 10, 10, 15],
}

# Median hours to claim by campaign type (pattern 5)
MEDIAN_CLAIM_HOURS = {
    "Research incentive": 9,
    "Survey incentive": 20,
    "Customer rebate": 30,
    "Referral bonus": 40,
    "Sales SPIF": 55,
    "Employee recognition": 96,
}

START = datetime(2026, 1, 1)
END = datetime(2026, 6, 30, 23, 59)
SNAPSHOT = datetime(2026, 6, 30, 23, 59)  # dataset "as of" date
N = 12000


def amount_claim_adjustment(amount):
    """Pattern 2: bigger payouts get claimed more (log-ish steps)."""
    if amount < 10:
        return -0.18
    if amount < 25:
        return -0.06
    if amount < 100:
        return 0.0
    if amount < 250:
        return 0.05
    return 0.08


def main():
    rows = []
    for i in range(1, N + 1):
        sender = random.choices(
            SENDERS, weights=[14, 8, 12, 7, 9, 5, 6, 5, 4, 6, 8, 4]
        )[0]
        campaign = random.choice(CAMPAIGNS)
        reward_type = random.choices(
            REWARD_TYPES, weights=[46, 22, 20, 12]
        )[0]
        amount = random.choice(AMOUNTS[campaign])

        issued = START + timedelta(
            seconds=random.random() * (END - START).total_seconds()
        )

        # Delivery: 97% delivered normally. Pattern 3: Northwind Traders
        # has a broken sending domain in March 2026 (25% delivered).
        p_delivered = 0.97
        if sender[1] == "Northwind Traders" and issued.month == 3:
            p_delivered = 0.25
        delivered = random.random() < p_delivered
        delivered_at = (
            issued + timedelta(minutes=random.randint(1, 45)) if delivered else None
        )

        # Reminders go to delivered-but-unclaimed payouts at 72 hours.
        # We decide the claim outcome in two stages so the reminder effect
        # (pattern 1) is real in the data, not just a label.
        p_claim = CLAIM_BASE[reward_type] + amount_claim_adjustment(amount)
        reminder_sent = False
        claimed_at = None
        if delivered:
            median_h = MEDIAN_CLAIM_HOURS[campaign]
            # Stage 1: claimed within the first 72 hours?
            if random.random() < p_claim * 0.72:
                hours = random.expovariate(1 / median_h)
                hours = min(hours, 71.9)
                claimed_at = delivered_at + timedelta(hours=hours)
            elif SNAPSHOT - delivered_at >= timedelta(hours=72):
                # Stage 2: reminder sent at 72h; reminded payouts claim
                # at a much higher rate than the unreminded baseline.
                reminder_sent = random.random() < 0.85
                p_late = 0.55 if reminder_sent else 0.22
                if random.random() < p_late * (p_claim / 0.85):
                    hours = 72 + random.expovariate(1 / 120)
                    claimed_at = delivered_at + timedelta(hours=hours)

        if claimed_at is not None and claimed_at > SNAPSHOT:
            claimed_at = None

        if claimed_at is not None:
            status = "claimed"
        elif not delivered:
            status = "delivery_failed"
        elif SNAPSHOT - issued >= timedelta(days=90):
            status = "expired_unclaimed"
        else:
            status = "pending_unclaimed"

        rows.append(
            {
                "payout_id": f"PO-{i:05d}",
                "issued_at": issued.strftime("%Y-%m-%d %H:%M:%S"),
                "sender_id": sender[0],
                "sender_name": sender[1],
                "sender_industry": sender[2],
                "campaign_type": campaign,
                "reward_type": reward_type,
                "amount_usd": f"{amount:.2f}",
                "recipient_country": random.choices(
                    ["US", "CA", "GB", "AU", "DE"], weights=[78, 8, 6, 4, 4]
                )[0],
                "delivered_at": delivered_at.strftime("%Y-%m-%d %H:%M:%S")
                if delivered_at
                else "",
                "reminder_sent": "true" if reminder_sent else "false",
                "claimed_at": claimed_at.strftime("%Y-%m-%d %H:%M:%S")
                if claimed_at
                else "",
                "status": status,
            }
        )

    out = "data/payouts.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
