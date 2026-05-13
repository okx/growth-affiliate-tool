---
name: tier-upgrade-candidates
description: |
  Use this skill when the user wants to find Regular-tier invitees who are doing whale-tier volume and should be offered a VIP upgrade. Triggers: "who should I push to VIP1", "tier upgrade candidates", "Regular users doing whale volume", "升级 VIP 名单", "fee tier candidates", "stealth VIPs". Do NOT use for finding low-tier users to nurture (use `high-potential-invitees`) or single-user prep (use `whale-deep-dive`).
---

# Tier upgrade candidates — stealth VIPs paying full commission

> "Who should I push to VIP1 this week?" / "找出应该升 VIP 的 Regular 用户"

Surfaces invitees whose current `feeTierRank` (Regular = "0") is below their actual trading
behavior, and ranks them by expected upside.

## When to use this skill

- User asks for upgrade candidates, VIP push list, 升级名单
- Weekly fee-tier review
- After a daily briefing flags Regular users in the top traders list
- Before a quarterly campaign to onboard whales into VIP perks

## What the agent does

### Step 1 — Pull last-30-day top traders by rebate

```json
{
  "name": "okx-affiliate-invitee-list",
  "arguments": {
    "page": "1", "limit": "95",
    "orderBy": "rebate", "orderDir": "desc",
    "periodType": "last_30d"
  }
}
```

### Step 2 — Filter to Regular tier with significant volume

Client-side filter:

```python
candidates = [
    r for r in rows
    if r["feeTierRank"] == "0"        # Regular
    and float(r["totalVol"]) >= 100_000  # ≥ $100K 30d volume
]
```

Adjust the volume threshold to the user's product:

| OKX VIP tier rough cutoff | 30-day volume | Typical fee tier achieved |
| ------------------------- | ------------- | ------------------------- |
| Casual                    | < $100K       | Regular                   |
| Soft VIP1 candidate       | $100K–$500K   | VIP1 if invited           |
| Hard VIP1 candidate       | > $500K       | VIP1 inevitable           |
| VIP2 candidate            | > $5M         | VIP2                      |

### Step 3 — For each candidate, pull deposit & lifetime context

For the top 10 candidates, call:

```json
{ "name": "okx-affiliate-invitee-detail", "arguments": { "uid": "<UID>" } }
```

Check:
- `joinTime` — how long they've been on
- `inviteeLevel` — current MLR level
- `wdAmt / depAmt` — withdrawal ratio (should be low for someone actively trading)
- `volMonth` — current calendar-month vol; flag if trending up

### Step 4 — Compute the upside

For each candidate, estimate the lift from a tier upgrade:

```
current_30d_commission = totalCommission (from list, period last_30d)
post_VIP1_commission ≈ current * 1.3   # Rough heuristic: VIP1 users trade ~30% more
                                       # because of fee discount; adjust to your data
expected_monthly_uplift = post_VIP1 - current
```

The exact multiplier varies; if the user has historical pre/post-upgrade data, use that.
Otherwise note the heuristic explicitly.

## Insights to extract

- **Total candidate pool size** — Regular users with > $100K 30d volume
- **Top 5 by expected uplift** — sorted by `current_30d_commission * heuristic_multiplier`
- **Stealth whales** — Regular users with > $1M 30d volume (these are unambiguous;
  upgrading them costs nothing and demonstrably retains them)
- **Mismatched MLR level** — `inviteeLevel: "2"` (your direct invitee) with `feeTierRank:
  "0"` but high volume — this is the most common case to fix

## Sample output format

```
🐳 VIP upgrade candidates — <YYYY-MM-DD>

📊 Pool summary
• Regular-tier users with > $100K 30d volume: N
• Of those, > $500K: M
• Estimated combined uplift after upgrade: $X,XXX/month

🔥 Top 10 candidates (by 30d rebate)

| # | UID         | 30d rebate | 30d volume | Lifetime rebate | Joined     | Recommendation |
| 1 | ...XXXXXX   | $XXX       | $X.XM      | $X,XXX           | YYYY-MM-DD | VIP1 fast-track |
| ...

🎯 Action plan
P0: <UIDs with > $500K 30d vol> — DM today with VIP1 offer + dedicated rep
P1: <UIDs with $100K–500K 30d vol> — batched outreach this week, mention specific volume
P2: monitor — users below $100K may be one-month spikes; recheck next week

💡 Talking points to include
1. Their current rebate rate / fee tier
2. The fee tier they're about to qualify for if you don't intervene
3. Concrete numbers from their last 30 days
4. The specific perks (lower fees, priority support, market analysis)
```

## Recommended follow-ups

- *"Draft a VIP upgrade pitch for UID …XXXXXX"*
- *"How is the post-upgrade cohort performing?"* — compare the volume of recently-upgraded
  users to their pre-upgrade trajectory using `acquisition-trends` with their first
  3 months pre/post
- *"What's the LTV multiple of VIP1 vs Regular for my node?"* — pull both cohorts and
  compute average lifetime commission per user

## Gotchas

- **`feeTierRank` is a string in the response** (`"0"` not `0`). Compare with string
  equality.
- **`feeTierRank` is OKX's global tier**, not your affiliate-side tier. Upgrading
  from `"0"` (Regular) to `"5"` (VIP1) requires the user to hit OKX's volume thresholds
  — your job is to nudge them and provide perks (dedicated rep, market analysis) that
  encourage the volume to come from your channel.
- **30-day volume can be spiky.** Don't promise a tier you can't deliver — recommend an
  outreach that builds the relationship; upgrade is the OKX system's decision.
- **The heuristic uplift multiplier is just an estimate.** If the user has actual
  pre/post-upgrade data, replace 1.3× with their measured number.
