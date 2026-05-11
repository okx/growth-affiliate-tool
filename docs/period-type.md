# `periodType` quick reference

The `periodType` parameter is shared across `okx-affiliate-performance-summary`,
`okx-affiliate-invitee-list`, and a few others. **Values are now strings, not integers.**

| Value         | Meaning                                                    |
| ------------- | ---------------------------------------------------------- |
| `last_7d`     | Last 7 days                                                |
| `last_30d`    | Last 30 days                                               |
| `this_month`  | This calendar month (UTC)                                  |
| `last_month`  | Last calendar month (UTC)                                  |
| `today`       | Today (current UTC day)                                    |
| `this_week`   | Current UTC week                                           |
| `total`       | All-time **(default — used when omitted)**                  |
| _omit_ + dates| Custom range — pass `begin` and `end` as Unix milliseconds  |

## Custom range example

Custom ranges no longer use `YYYY-MM-DD`. Pass **Unix milliseconds** as strings:

```json
{
  "begin": "1775001600000",
  "end":   "1777593599000"
}
```

Both are inclusive. Example above is `2026-04-01 00:00:00 UTC` → `2026-04-29 23:59:59 UTC`.

You can omit `periodType` entirely when passing `begin` + `end`. The server treats any
`periodType` value it does not recognize (including absence) as "use the supplied range".

## Notes

- All time-based aggregates use UTC day boundaries. `today` = `<today> 00:00 UTC` →
  `<today> 23:59:59 UTC`.
- `begin` and `end` are **inclusive** and use Unix ms. Be careful with the `end` boundary —
  for "all of April 2026" pass `2026-04-30 23:59:59 UTC` (`1777823999000`), not
  `2026-05-01 00:00:00 UTC`.
- The endpoint exposes data starting from the date your affiliate account was first
  activated. Custom ranges that begin before that date are silently clamped to activation.
- For multi-day trends, prefer many small custom ranges over one big one — it lets you spot
  daily anomalies without losing precision.

## Common mistakes

| Mistake                                    | Fix                                                    |
| ------------------------------------------ | ------------------------------------------------------ |
| Passing integer `5` for `periodType`       | Use string `"total"`                                    |
| Using `YYYY-MM-DD` for `begin`/`end`       | Convert to Unix ms — `Date.UTC(2026, 3, 1)` in JS, `int(datetime(2026,4,1).timestamp()*1000)` in Python |
| Off-by-one second on `end`                 | Use `<day> 23:59:59 UTC`, not `<next day> 00:00:00`     |
| Passing year 2025 ms when meant 2026       | Double-check year — `1743465600000` is **2025-04-01**, not 2026-04-01 |
