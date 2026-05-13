---
name: whale-deep-dive
description: |
  Use this skill when the user wants everything known about a single invitee — lifetime totals, recent activity, KYC details, deposit/withdrawal history, and what to do next. Triggers: "pull up UID X", "give me everything on user Y", "deep dive on Z", "prep me to DM user A", "what's user B's history", "show me X's last 30 days". The user usually provides a UID inline. Do NOT use for multi-user lists (use `high-potential-invitees` or `churn-rescue` instead).
---

# Whale deep dive — single user history & state

> "Pull everything on UID 743072917935893796" / "prep me to DM this user"

A focused, conversational rundown of one invitee with enough context for the user to send
a credible outreach message.

## When to use this skill

- User provides a specific UID (or unambiguously points to one user from a prior list)
- User asks to "drill into" a user from a list output
- Before sending an outreach DM
- Investigating an anomaly (sudden volume spike or drop on a specific account)

## What the agent does

### Step 1 — Lifetime detail

```json
{ "name": "okx-affiliate-invitee-detail", "arguments": { "uid": "<UID>" } }
```

Returns:
- `affiliateCode` — which channel they came through
- `region`, `level`, `inviteeLevel`, `inviteeRebateRate`
- `joinTime`, `kycTime`, `firstTradeTime`
- `depAmt`, `wdAmt` — lifetime deposits and withdrawals
- `totalVol`, `totalCommission`, `accFee` — lifetime trading
- `volMonth` — current calendar-month volume

If the call returns `code: 51621 "The user isn't your invitee"`, stop — either the UID is
typo'd or they aren't yours. Suggest the user double-check.

### Step 2 — Period slices

Pull the user's activity in `last_30d`, `last_7d`, and `today` to spot the current trend.
The `okx-affiliate-invitee-detail` endpoint is lifetime-only, so the agent uses
`invitee-list` and filters to the target UID client-side:

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

Paginate until the target UID is found (or until the data array is empty). If the UID
doesn't appear in last_30d top 95, they're effectively dormant for the period.

Repeat for `last_7d` and (if relevant) `today`.

### Step 3 — Compute derived signals

| Signal                          | Formula                                                    | Why it matters                            |
| ------------------------------- | ---------------------------------------------------------- | ----------------------------------------- |
| Months since join               | `(now - joinTime) / 30 days`                                | Sets the baseline run-rate                 |
| Avg monthly rebate (lifetime)   | `totalCommission / months_since_join`                       | Run-rate to compare current to            |
| Activity trend                  | `last_7d_rebate / last_30d_rebate * 4.3`                    | >1 = accelerating; <1 = slowing           |
| Withdrawal ratio                | `wdAmt / depAmt`                                            | >0.7 = exiting; <0.1 = parked              |
| Current-month engagement        | `volMonth / (totalVol / months_since_join)`                  | <0.1 = effectively idle this month         |

### Step 4 — Find their invite link / channel context

Cross-reference `affiliateCode` with `okx-affiliate-link-list` to see how the channel as a
whole is doing — was this user a one-off win or part of a productive cohort?

## Insights to extract

- **Whale status** — lifetime rebate ≥ $5K → whale; $1K–5K → mid-tier; < $1K → retail
- **Health** — accelerating / steady / slowing / dormant
- **Capital intent** — actively depositing more / parked / cashing out
- **Outreach hook** — concrete reason this user matters to the operator (recent
  fee tier upgrade? big deposit? hit a milestone like first $1M volume?)

## Sample output format

```
🐋 User profile — UID …XXXXXX

📋 Identity
• Region: <country>
• Joined: <YYYY-MM-DD> (<N> months ago)
• Channel: <affiliateCode>
• VIP tier: <level> (rebate rate <X>%)
• KYC verified: <YYYY-MM-DD>
• First trade: <YYYY-MM-DD> — activated <N> days after join

💰 Lifetime totals
• Deposited: $X,XXX,XXX
• Withdrawn: $X,XXX,XXX (X%)
• Capital on platform: $XXX,XXX
• Trading volume: $X.XXM
• Commission to you: $X,XXX (lifetime), avg $XXX/month

📈 Recent activity
• Last 30 days: $X rebate / $XK volume
• Last 7 days:  $X rebate / $XK volume
• This month so far: $X rebate
• Trend: <accelerating / steady / slowing / dormant>

🎯 Outreach prep
• Hook: "<specific concrete reason this user matters>"
• Risk: "<bag-sitter? VIP1-ready Regular? possible churn? cash-out signal?>"
• Suggested message angle: <one line>
```

## Recommended follow-ups

- *"Draft a DM to this user"* — based on outreach prep
- *"Pull other users from the same channel"* — switch to `acquisition-trends` filtered by
  `affiliateCode`
- *"Compare this user to my top 3 whales"* — call the skill again for each whale and
  produce a side-by-side
- *"When did they last trade?"* — see `churn-rescue` step 5 (probe backward in 30-day
  windows; expensive)

## Gotchas

- **`invitee-detail` is lifetime-only** — to get any period slice for a single user you
  must paginate the period-scoped `invitee-list` and filter client-side. `keyword`
  filter is broken in the current MCP — do not rely on it.
- **`volMonth` resets at UTC start of each calendar month.** On the 1st of the month it
  will be ~$0 for everyone; don't conclude churn from this alone.
- **Withdrawal ratio is lifetime.** A user can have a 70% withdrawal ratio because of one
  big cash-out a year ago, then re-deposit and stay active. Cross-check with `volMonth`
  before concluding.
- **`accFee` (lifetime fees paid by user) is roughly 3× `totalCommission`** at default
  rebate rates. If the ratio is off, the user is on a non-standard rebate split — pull
  `inviteeRebateRate` to see.
