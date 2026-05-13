---
name: daily-briefing
description: |
  Use this skill when the user wants yesterday's (or today-so-far) affiliate node performance — commission, deposits, new invitees, top traders, top depositors, and action items for the day. Triggers: "yesterday's data", "morning report", "daily briefing", "节点日报", "看下昨日表现", "今天节奏怎么样", "EOD report", "where am I at today". Do NOT use for multi-week or quarterly trends (use `acquisition-trends` instead). Do NOT use for a single user deep dive (use `whale-deep-dive`).
---

# Daily briefing — yesterday's affiliate node performance

> "Show me yesterday's data" / "看下昨日节点数据"

A concise EOD-style report that combines aggregate performance with a tight list of action
items the user can execute in the next 24 hours.

## When to use this skill

- User explicitly asks for "yesterday", "today so far", "morning briefing", "EOD", "日报"
- Daily 1:1 cadence with the affiliate operator
- Right before a community post / push notification window
- After a market event when the user wants to size up the impact

## What the agent does

Make these calls in parallel (rate-limit-friendly: ≤ 5 RPS):

### 1. Yesterday's headline numbers

```json
{
  "name": "okx-affiliate-performance-summary",
  "arguments": {
    "begin": "<yesterday 00:00:00 UTC in ms>",
    "end":   "<yesterday 23:59:59 UTC in ms>"
  }
}
```

### 2. Today-so-far (for live-pace comparison)

```json
{ "name": "okx-affiliate-performance-summary", "arguments": { "periodType": "today" } }
```

### 3. Last 7 days (context window)

```json
{ "name": "okx-affiliate-performance-summary", "arguments": { "periodType": "last_7d" } }
```

### 4. Yesterday's top commission contributors

```json
{
  "name": "okx-affiliate-invitee-list",
  "arguments": {
    "page": "1", "limit": "10",
    "orderBy": "rebate", "orderDir": "desc",
    "begin": "<yesterday begin ms>", "end": "<yesterday end ms>"
  }
}
```

### 5. Yesterday's top depositors

```json
{
  "name": "okx-affiliate-invitee-list",
  "arguments": {
    "page": "1", "limit": "10",
    "orderBy": "depAmt", "orderDir": "desc",
    "begin": "<yesterday begin ms>", "end": "<yesterday end ms>"
  }
}
```

### 6. Newest invitees (to spot which ones joined yesterday)

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

Filter rows whose `joinTime` falls within yesterday's UTC window — these are the new
invitees from yesterday.

## Insights to extract

For each top depositor, **flag bag-sitters** (`depAmt > 0` && `totalVol < depAmt * 5`).
These are 24-hour rescue priorities.

For each top trader on Regular tier, **flag VIP1 upgrade candidates** (`feeTierRank == "0"`
+ `totalVol > $100K` in the day). They're paying you full commission rates while doing
whale-tier volume — give them the discount.

For new invitees, compute **same-day deposit rate** and **same-day activation rate** —
useful health metrics for the acquisition channel.

Compare yesterday's commission to the 7-day daily average to call out under/over-performance
in plain language.

## Sample output format

```
📊 Daily briefing — <YYYY-MM-DD>

📍 Yesterday at a glance
• Commission: $XXX.XX (Spot $X / Derivative $X / BSC $X)
• Volume: $X.XXM (XX% derivatives)
• Deposits: $X,XXX
• Active traders: XX (Der X / Spot X)
• New invitees: X | First-time traders: X

📅 Vs context
• 7-day daily avg: $XXX → yesterday was +/- XX%
• Today so far (X hours in): $XX → on track for ~$XXX EOD

🐋 Yesterday's top 5 by rebate
| UID | Tier | Rebate | Volume |
| ... | ...  | ...    | ...    |

💵 Yesterday's depositors
✅ Same-day activated: <list with vol>
⚠️ Bag-sitters (deposited, didn't trade): <list>

🆕 New invitees
<count> joined, of which <X> deposited and <Y> traded same-day

🎯 Action items
1. Rescue bag-sitters within 24h: <UIDs>
2. VIP1 upgrade candidates: <UIDs>
3. <Anything anomalous: 0 new invitees N days in a row, sudden spike, etc.>
```

## Recommended follow-ups

After the briefing, offer one of:

- *"Drill into top contributor UID …XXXXXX"* → switch to `whale-deep-dive`
- *"Why did commission drop / spike vs avg?"* → switch to `acquisition-trends` or pull
  per-link `commission24h` from `okx-affiliate-link-list`
- *"List me all bag-sitters from the last 7 days, not just yesterday"* → switch to
  `high-potential-invitees` with the bag-sitter filter

## Gotchas

- **Custom-range timestamps are Unix milliseconds**, not `YYYY-MM-DD`. Year matters —
  `1743465600000` is **2025-04-01**, not 2026.
- **`begin` is inclusive at 00:00:00; `end` is inclusive at 23:59:59**. Off-by-one second
  matters when comparing day-on-day.
- **Yesterday's data may still be settling at UTC midnight**. The `uTime` field on the
  response tells you the freshness. If `uTime` is < 1 hour past midnight UTC, the numbers
  may revise upward as late trades clear.
- **No `total` field in invitee-list responses** — for "yesterday's depositors total", count
  the rows you get and paginate until empty if needed.
