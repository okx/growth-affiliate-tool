---
name: high-potential-invitees
description: |
  Use this skill when the user wants a curated list of invitees worth nurturing — fresh deposits without trading, mid-tier traders showing momentum, KYC-verified users who haven't deposited, recently activated whales. Triggers: "find high potential users", "who should I reach out to", "潜力用户", "give me a list of users to nurture", "rescue list", "high LTV candidates". Also use when the user asks for a multi-tier prioritization (P0/P1/P2). Do NOT use for a single user deep dive (use `whale-deep-dive`) or for a generic daily briefing (use `daily-briefing`).
---

# High-potential invitees — multi-tier prioritization

> "Who should I reach out to today?" / "潜力用户清单"

Builds a tiered list of invitees worth contacting in the next 24–72 hours, sorted by
expected return on outreach effort.

## When to use this skill

- User wants an actionable outreach list, not raw data
- User mentions "potential", "nurture", "rescue", "activation", "潜力"
- User wants P0/P1/P2 prioritization
- Right after a daily briefing flags concerns the user wants to act on

## What the agent does

The MCP has no built-in "high potential" filter, so the agent pulls several lenses and
intersects them client-side.

### Lens A — recent depositors with no trading (P0 rescue)

```json
{
  "name": "okx-affiliate-invitee-list",
  "arguments": {
    "page": "1", "limit": "50",
    "orderBy": "depAmt", "orderDir": "desc",
    "periodType": "last_7d"
  }
}
```

Filter rows where `depAmt > 0 && totalVol < depAmt * 5`. These have fresh capital and need
a nudge within 24–48 hours before they cash out or stay dormant.

### Lens B — top traders with growing volume (P1 VIP-upgrade candidates)

```json
{
  "name": "okx-affiliate-invitee-list",
  "arguments": {
    "page": "1", "limit": "30",
    "orderBy": "rebate", "orderDir": "desc",
    "periodType": "last_30d"
  }
}
```

Filter rows where `feeTierRank == "0"` (Regular) AND `totalVol > 100000`. They're paying
full commission while doing whale-tier volume — give them VIP1 and they'll trade more.

### Lens C — newly joined and producing (P0 star activators)

Pull the newest invitees (last 7 days) sorted by lifetime rebate:

```json
{
  "name": "okx-affiliate-invitee-list",
  "arguments": {
    "page": "1", "limit": "30",
    "orderBy": "cTime", "orderDir": "desc",
    "periodType": "total"
  }
}
```

From those rows, keep only ones whose `joinTime` is within the last 7 UTC days, then sort
by `totalCommission` descending. The top 3–5 with non-trivial volume in their first week
are the "star activators" — they're already paying and most likely to scale.

### Lens D — KYC-verified, never deposited (P3 soft-conversion)

```json
{
  "name": "okx-affiliate-invitee-list",
  "arguments": {
    "page": "1", "limit": "50",
    "kycStatus": "verified",
    "orderBy": "cTime", "orderDir": "desc",
    "periodType": "total"
  }
}
```

Filter rows where `depAmt == "0"`. These users passed compliance but never funded — usually
the cheapest cohort to convert with a first-deposit bonus.

## Insights to extract

- **Combined size of P0 + P1** (rescue + tier-upgrade) — this is the realistic
  outreach workload for the day
- **Star activators concentration** — if 1–2 new joiners are producing > 50% of weekly
  rebate, the channel is producing high-quality leads; ask the user what changed in
  acquisition
- **P3 size vs total invitees** — high P3 share (>15%) means the funnel is leaking at
  first-deposit; suggest a deposit-bonus campaign

## Sample output format

```
🎯 High-potential invitees — <YYYY-MM-DD>

🔥 P0 — Rescue (deposited last 7d, didn't trade)
| UID         | Joined     | Deposit | Volume | Days idle |
| ...XXXXXX   | YYYY-MM-DD | $X,XXX  | $0     | N         |

Action: 24–48h DM with first-trade rebate or Flash Earn pitch.

🐋 P1 — VIP1 upgrade candidates (Regular tier, >$100K 30d volume)
| UID         | 30d rebate | 30d volume |
| ...XXXXXX   | $XX        | $XXXK      |

Action: personal outreach with VIP fee tier offer.

⭐ P0 — Star activators (joined ≤7d, already producing)
| UID         | Joined     | 7d rebate | 7d volume |
| ...XXXXXX   | YYYY-MM-DD | $XX       | $XXXK     |

Action: VIP1 fast-track + direct line for trading questions. Lock them in before
competitors find them.

🆕 P3 — KYC done, no deposit yet (top 10 most recent)
| UID         | KYC date   | Days since KYC |
| ...XXXXXX   | YYYY-MM-DD | N              |

Action: drip campaign with first-deposit bonus.

📊 Scoreboard
| Cohort                | Users | Recommended response time |
| P0 rescue             | X     | 24h                       |
| P1 VIP1 candidates    | X     | This week                 |
| P0 star activators    | X     | Today                     |
| P3 soft conversion    | X     | Drip / weekly digest      |
```

## Recommended follow-ups

- *"Pull the full lifetime history on UID …XXXXXX"* → switch to `whale-deep-dive`
- *"Generate outreach scripts for each tier"* → write per-tier DM templates
- *"How is this week's P0 list trending vs last week?"* → re-run the skill with last week's
  custom date range and diff

## Gotchas

- **`hasDeposit` / `hasTrade` filters were removed in the new MCP** — you must filter
  client-side after pulling the list.
- **`keyword` is currently broken** (returns same rows regardless of input) — do not try
  to filter by UID via the API; pull list and filter client-side.
- **Star activator window**: use 7 days, not 24 hours — same-day volume on a fresh account
  is too small to rank meaningfully.
- **Don't paginate past `limit: "95"`** — the API returns 500 on `limit ≥ 99`.
