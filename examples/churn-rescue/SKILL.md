---
name: churn-rescue
description: |
  Use this skill when the user wants to find churning or sleeping users — whales who stopped trading, depositors whose activity dropped, or recently active users showing decline. Triggers: "find churning users", "who's slipping away", "流失预警", "鲸鱼跑了", "sleeping whales", "show me users with declining volume", "last seen", "when did user X stop trading". Do NOT use this for net-new acquisition analysis (use `acquisition-trends`) or for users who are still healthy (use `whale-deep-dive`).
---

# Churn rescue — find users slipping away

> "Which whales are leaking?" / "流失预警 / 找出停止交易的用户"

Identifies users whose activity has degraded materially, segments them by stage of decay,
and prioritizes by lifetime value at stake.

## When to use this skill

- User asks about churn, slipping, sleeping, rescue, 流失, 沉睡
- After a daily briefing flags a downward trend in active trader count
- Quarterly retention review
- Before a re-engagement campaign

## What the agent does

There is no `lastTradeTime` field exposed by the MCP, so the agent has to infer "last
active" by comparing lifetime totals to recent-window activity.

### Step 1 — Pull lifetime top contributors

```json
{
  "name": "okx-affiliate-invitee-list",
  "arguments": {
    "page": "1", "limit": "50",
    "orderBy": "rebate", "orderDir": "desc",
    "periodType": "total"
  }
}
```

This is the "all-time whales" baseline.

### Step 2 — Pull last-30-day top contributors

```json
{
  "name": "okx-affiliate-invitee-list",
  "arguments": {
    "page": "1", "limit": "50",
    "orderBy": "rebate", "orderDir": "desc",
    "periodType": "last_30d"
  }
}
```

This is the "currently active whales" set.

### Step 3 — Diff and classify

For each UID in the lifetime top set, compute:

- `decay_ratio = 1 - (last30_rebate / (lifetime_rebate / months_since_join))`

Bucket users:

| Bucket               | Decay signal                                                        | Action priority |
| -------------------- | ------------------------------------------------------------------- | --------------- |
| Healthy              | last30 rebate ≥ 80% of expected monthly run-rate                    | none            |
| Slowing              | last30 rebate is 30–80% of run-rate                                 | watch           |
| Decaying             | last30 rebate is 5–30% of run-rate                                  | reach out       |
| Effectively churned  | last30 rebate < 5% of run-rate, or user not in last30 top 50 at all | urgent          |

### Step 4 — For each decayed/churned user, get withdrawal ratio

For the top 5 candidates, call:

```json
{ "name": "okx-affiliate-invitee-detail", "arguments": { "uid": "<UID>" } }
```

Compute `wdAmt / depAmt`. This separates two churn modes:

- `wdAmt / depAmt > 0.7` — **Type A: cashed out**, hard to win back
- `wdAmt / depAmt < 0.1` and `volMonth ≈ 0` — **Type B: parked & idle**, easiest to win back
  (capital still on platform)
- Otherwise — **Type C: gradual disengagement**

### Step 5 — Optional: probe when they last traded

The new MCP does not expose `lastTradeTime`. To approximate, run `invitee-list` with a
1-month custom date range moving backward:

```json
{
  "name": "okx-affiliate-invitee-list",
  "arguments": {
    "page": "1", "limit": "50",
    "orderBy": "rebate", "orderDir": "desc",
    "begin": "<one month ago in ms>",
    "end": "<two months ago in ms>"
  }
}
```

Check whether the UID appears with nonzero `totalVol`. Walk backward in 30-day chunks until
you find activity. This is expensive — only do it for the top 5 users you actually plan to
DM.

## Insights to extract

- **Total LTV at risk** — sum lifetime rebate across decaying + churned users
- **Largest single whale at risk** — flag if any one user's lifetime rebate exceeds 5% of
  the node's total
- **Type A vs Type B ratio** — if mostly Type B (capital still on platform), reactivation
  is feasible; if mostly Type A, the channel may have a quality problem
- **Decay timing pattern** — if multiple users decayed in the same calendar month, look for
  an event (market crash, OKX policy change, competitor campaign)

## Sample output format

```
⚠️ Churn watchlist — <YYYY-MM-DD>

📊 At-a-glance
• Lifetime top 50 users: 50
• Of those, currently active (last 30d top 50): X
• Effectively churned: Y
• Combined LTV at risk: $X,XXX,XXX

🔴 Type A — cashed out (urgent, but hard to win back)
| UID | Lifetime rebate | Withdrawal ratio | Last seen |
| ...XXXXXX | $XXX,XXX | 95% | YYYY-MM |

🟡 Type B — parked & idle (easiest win)
| UID | Lifetime rebate | Capital parked | Last seen |
| ...XXXXXX | $XX,XXX | $X,XXX,XXX | YYYY-MM |

🟠 Type C — gradual disengagement (intervene now)
| UID | Lifetime rebate | Recent trend |
| ...XXXXXX | $XX,XXX | declining MoM for N months |

🎯 Action plan
P0: <UIDs> — Type B users with parked capital, DM with VIP perks or Flash Earn pitch
P1: <UIDs> — Type C users still active, send market analysis to nudge them
P2: <UIDs> — Type A users, send exit survey to learn why they left
```

## Recommended follow-ups

- *"Generate outreach scripts for each bucket"*
- *"What did we do differently in <peak month>?"* — switch to `acquisition-trends` and
  compare peak month behavior
- *"Pull full history on the largest at-risk user"* → `whale-deep-dive`

## Gotchas

- **No `lastTradeTime` field exists.** Inferring it from period queries is slow and
  approximate. Don't burn API budget probing > 5 users.
- **Withdrawal ratio is lifetime, not period-scoped.** A user with `wdAmt / depAmt = 0.7`
  may have withdrawn the bulk months ago and recently re-deposited. Cross-check with
  `volMonth` for current activity.
- **Be conservative on "churned" labels.** Volume can be lumpy — a single quiet month does
  not equal churn. Require ≥ 2 quiet months in a row, or a clear withdrawal pattern.
- **`subAffiliateUid` filter is broken** in the current MCP — to attribute churn to a
  sub-affiliate downline, filter client-side after pulling the list.
