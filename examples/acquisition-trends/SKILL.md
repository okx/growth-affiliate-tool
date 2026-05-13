---
name: acquisition-trends
description: |
  Use this skill when the user wants to analyze acquisition or performance trends over multiple months — new invitees per month, conversion rate trajectory, monthly commission, daily-active-trader trends. Triggers: "拉新趋势", "近 N 个月的拉新", "monthly trend", "show me the last 6 months", "DAT history", "when was my peak", "analyze acquisition over time", "what's the YoY". Do NOT use for single-day briefings (use `daily-briefing`) or single-user history (use `whale-deep-dive`).
---

# Acquisition trends — multi-month performance analysis

> "分析下我过去 6 个月的拉新情况" / "show me the last 12 months"

Time-series view of the affiliate node: new invitees, activation rates, deposits, volume,
commission, and active-trader counts. Surfaces inflection points and the events behind
them.

## When to use this skill

- User asks for trends, history, MoM, QoQ, YoY analysis
- Quarterly review / pitch deck preparation
- Investigating a sudden change ("why is commission down 30% this month?")
- Replicating a past success ("what did we do in August?")

## What the agent does

### Step 1 — Choose the window

Default to 12 months if user says "trend" / "history" without a number. For specific
requests like "last 6 months" or "Q1 2026" honor that exactly.

### Step 2 — One call per calendar month

Loop over each month in the window:

```json
{
  "name": "okx-affiliate-performance-summary",
  "arguments": {
    "begin": "<month start ms>",
    "end":   "<month end ms>"
  }
}
```

Cap parallelism at ≤ 5 concurrent calls; the endpoint rate-limits with `code: 50011`.
Insert a 200–500 ms delay between batches.

### Step 3 — For finer-grained trends, pull daily data

If the user asks for daily-active-trader (DAT) history or wants to identify peak days, loop
day-by-day over the window:

```json
{
  "name": "okx-affiliate-performance-summary",
  "arguments": {
    "begin": "<day 00:00:00 UTC ms>",
    "end":   "<day 23:59:59 UTC ms>"
  }
}
```

90 days = 90 calls. Run serially with `sleep 0.4` between requests to avoid 429s. For >180
days, suggest the user request only monthly granularity unless they truly need the daily
resolution.

### Step 4 — Cache aggregates

Save results as CSV (one row per period) for follow-up analysis without re-pulling:

```
date,invitees,firstTimeTrader,traderCnt,depAmt,vol,commission
```

Use the `details[]` array from the response to sum across SPOT/DERIVATIVE/BSC.

## Insights to extract

- **Direction of travel** — first 30 days vs middle 30 vs last 30. Quote the deltas.
- **Peak month and peak day** — the highest value of each metric and the date
- **Acquisition velocity vs commission lag** — new invitees in month M often produce most
  of their commission in months M+1 to M+3; surface this lag if it's pronounced
- **Activation rate trend** — `firstTimeTrader / invitees` per month. Healthy nodes hold
  this ratio above 40%; below 30% signals quality erosion
- **Volume-per-trader trend** — total `vol` / `traderCnt`. Falling per-trader volume with
  steady trader count = users trading smaller (market conditions or product-mix shift)
- **Spot vs derivatives mix drift** — if derivatives share is climbing, the user base is
  getting more risk-tolerant; useful for product recommendations
- **Concentration risk** — % of monthly commission from the top 3 users. If > 50% the node
  is fragile

## Sample output format

```
📊 Acquisition trend — <START> to <END> (<N> months)

📈 Monthly snapshot
| Month   | New inv | First-time | Activation | Deposit | Volume | Commission |
| 2025-06 |     338 |        135 |        40% |  $2.13M | $756M  | $61,970    |
| ...

📊 Quarterly view
• Q2 (M–M): X new / Y first / $Z commission — strongest acquisition quarter
• Q3 (M–M): ...
• ...

🏔️ Peaks
• Peak monthly new invitees: <N> in <YYYY-MM>
• Peak monthly commission: $X in <YYYY-MM>
• Peak DAT day: <N> traders on <YYYY-MM-DD>

🔍 Key insights
1. <inflection point with date and likely cause>
2. <activation rate trend>
3. <commission concentration>
4. <volume-per-trader drift>

📌 Suggested action
<one paragraph: what to replicate from the best period, what to watch in the current
period, where to focus the next 30 days>

📁 Raw data
CSV with daily/monthly rows saved at <path>. Useful for replay against BTC price,
campaign timestamps, etc.
```

## Recommended follow-ups

- *"Why did <month> spike?"* — pull the channel-level (`okx-affiliate-link-list`) data for
  that month to see if a specific link drove it
- *"Cross-reference with BTC price"* — pull a price chart from blockbeats and overlay
- *"Who were the top users in <peak month>?"* — re-run `high-potential-invitees` with
  the peak month's date range and see if they're still active

## Gotchas

- **Custom-range timestamps are Unix milliseconds** in UTC. `int(datetime(2026,4,1).timestamp()*1000)`
  in Python. Off-by-year mistakes are common.
- **Months have different lengths** — when comparing MoM, normalize daily averages or be
  explicit about absolute vs. per-day numbers.
- **The endpoint returns 429 above ~5 RPS**, then succeeds again seconds later. Build retry
  logic with exponential backoff; do not panic on a single 429.
- **`okx-affiliate-sub-affiliate-list` is lifetime-only** in the new MCP — for time-windowed
  sub-affiliate analysis pull `invitee-list` with `subAffiliateUid`... but that filter is
  currently broken, so client-side filtering is needed.
- **For long backfills**, consider chunked monthly calls (12–24 calls) rather than daily
  (300+ calls). The user usually wants the shape, not every day.
