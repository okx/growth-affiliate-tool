# FAQ

Common errors and questions, with the actual fix.

## Authentication

### Q: I authenticated but every tool call returns empty data.

The OAuth account you signed in with is **not** the OKX account that is enrolled as an
Affiliate. The MCP only sees data for the connected affiliate.

**Fix:**
1. Sign out / revoke the wrong account at OKX → *Settings → Connected apps*.
2. Re-run your client's MCP auth command (`/mcp` in Claude Code).
3. Sign in with the correct affiliate account on the OKX consent page.

### Q: My tool calls return 401 hours after install.

The OAuth `access_token` lifetime is approximately **1 hour**. Native-OAuth clients refresh
automatically — if you still see 401s after a retry, your client may have lost the
`refresh_token`.

**Fix:** Re-run your client's MCP auth command. You will breeze through the consent screen
without any prompts because OKX still has the grant on file.

### Q: I see `invalid_grant: resource does not match`.

Your MCP client is not adding the required `resource` parameter to OAuth requests
([RFC 8707](https://datatracker.ietf.org/doc/html/rfc8707)).

**Fix:** Use a client that handles this natively (Claude Code, Codex, Hermes, Cursor are all
known to work). For OpenClaw, use the bundled [skill workaround](install/openclaw.md).

### Q: How do I revoke the OAuth grant?

OKX → *Settings → Connected apps* → find your MCP server entry → *Revoke*. The
`access_token` and `refresh_token` will both stop working immediately.

---

## Tool errors

### Q: I get a 500 `system error` from `okx-affiliate-invitee-list`.

The endpoint returns 500 when `limit ≥ 99`, even though the schema says max is 100. Bug
acknowledged; pending OKX-side fix.

**Fix:** Use `limit: "95"` or lower. For larger result sets, paginate.

### Q: I passed `linkType: "whatever"` and still got all results.

`okx-affiliate-link-list` and `okx-affiliate-co-inviter-list` **silently accept invalid
enum values** for `linkType` / `linkStatus` and return all rows. Case-sensitive too —
`STANDARD` is not the same as `standard`.

**Fix:** Pass only the documented lowercase values: `standard` / `co_inviter`,
`normal` / `abnormal`. After calling, sanity-check the returned `linkType` / `linkStatus`
matches what you asked for.

### Q: The response doesn't have a `total` count. How do I paginate?

Correct — the response does not include a total or `hasNextPage` field.

**Fix:** Page through until you get an empty `data` array. Pseudo-code:

```python
page = 1
all_rows = []
while True:
    r = call("okx-affiliate-invitee-list", {"page": str(page), "limit": "95", ...})
    rows = r["data"]
    if not rows:
        break
    all_rows.extend(rows)
    page += 1
```

If you know you need only top N, set `limit` and call once. Avoid pulling more data than
needed — rate limits are tight (~5 RPS).

### Q: 429 Too Many Requests.

You are hitting the per-account rate limit. Bursting more than ~5 requests per second
returns `code: 50011`.

**Fix:** Space your calls (a 200–500 ms delay between requests works for most workloads).
If you are pulling a large multi-month trend, prefer fewer larger ranges over many small
daily calls.

### Q: `okx-affiliate-invitee-detail` returns "The user isn't your invitee".

Code `51621` is returned for both *"valid UID but not your invitee"* and *"malformed UID"*.
The distinction is not exposed.

**Fix:** Verify the UID via `okx-affiliate-invitee-list` first. If it does not appear in
your list, this MCP cannot return data for it.

### Q: `okx-affiliate-performance-summary` returns 400 on a custom date range.

Most likely your `begin` / `end` timestamps are wrong.

**Fix:** Confirm both are passed, both are **Unix milliseconds** (not seconds, not
YYYY-MM-DD), and the year is correct. `1743465600000` is **2025**-04-01, not 2026-04-01.

---

## Scope and permissions

### Q: Should I grant Trade / Earn / Asset Transfer scopes?

**No.** This MCP is read-only. Granting write scopes is unnecessary and only widens the
blast radius if your token leaks. The recommended config is *Live Trading → Read-only* and
nothing else.

### Q: Can I use my Demo trading account?

The MCP server does not currently expose demo affiliate data. The OAuth flow lets you toggle
the *Demo trading* scope, but tool calls will return empty for demo-only accounts. Use a
live affiliate account.

---

## Data semantics

### Q: Are the timestamps UTC?

Yes. `joinTime`, `firstTradeTime`, `kycTime`, `uTime`, `cTime` are all Unix **milliseconds**
in UTC.

### Q: Are the financial fields period-scoped or lifetime?

It depends on the tool:

- `okx-affiliate-performance-summary` — period-scoped (`periodType` chooses the window;
  `total` is lifetime).
- `okx-affiliate-invitee-list` — period-scoped per row (`depAmt`, `totalFee`,
  `totalCommission`, `totalVol` apply to the requested `periodType`).
- `okx-affiliate-invitee-detail` — **lifetime totals** (no `periodType` parameter), plus
  `volMonth` for the current calendar-month volume.
- `okx-affiliate-sub-affiliate-list` — **lifetime only** (new schema removed the period
  filter for sub-affiliates).

### Q: Why are some fields decimal strings, not numbers?

To preserve precision. Affiliate balances and trading volumes can have many significant
digits; converting to a JSON number can lose precision in some clients. Always parse as
`Decimal` / `BigDecimal` if you do arithmetic on them.

### Q: How fresh is the data?

The `uTime` field on every response tells you when OKX last refreshed the underlying
aggregates. Snapshots typically lag real-time by 30–60 minutes for high-fanout metrics like
`traderCnt` and `vol`. New invitees and deposits appear within a few minutes.

### Q: Where did `hasDeposit` / `hasTrade` / `countryCode` filters go?

Removed in the recent MCP overhaul. To find "deposited but never traded" cohorts, pull the
invitee list and filter client-side (`depAmt > 0 && totalVol === 0`). For country filtering,
filter the response by the `country` field.

---

## Operational

### Q: Where is the token stored?

It depends on the client:

- **Claude Code** — encrypted in `~/.claude/state.json` (or platform keychain on macOS).
- **Codex / Hermes / Cursor** — see your client's docs; usually a per-app config dir.
- **OpenClaw (via skill)** — `~/.openclaw/data/okx-affiliate-mcp/token.json` in plain JSON.

### Q: Can I share the token with a teammate?

**No.** OAuth tokens are tied to a single OKX account. Each teammate completes their own
OAuth flow.

### Q: I changed the OKX password / 2FA. Do I need to re-auth?

OKX may invalidate active OAuth grants when you reset credentials. If you start seeing 401s
after a security change, re-run `/mcp` to mint new tokens.
