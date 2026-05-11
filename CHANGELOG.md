# Changelog

## 2026-05-11 — sync with new MCP schema (BREAKING)

OKX rolled out a major MCP update with renamed tools, restructured parameters, and a
restructured response. This release brings the documentation in line.

### Tool names

| Old                                | New                                   |
| ---------------------------------- | ------------------------------------- |
| `affiliate-performance-summary`    | `okx-affiliate-performance-summary`   |
| `affiliate-invitee-list`           | `okx-affiliate-invitee-list`          |
| `affiliate-invitee-detail`         | `okx-affiliate-invitee-detail`        |
| `affiliate-link-list`              | `okx-affiliate-link-list`             |
| `affiliate-sub-affiliate-list`     | `okx-affiliate-sub-affiliate-list`    |
| `affiliate-co-inviter-list`        | `okx-affiliate-co-inviter-list`       |

> The `affiliate-pro-*` names that appeared in earlier draft docs were never live in
> production. The current production prefix is `okx-affiliate-*`.

### Parameter changes

All numeric parameters are now strings (e.g. `"page": "1"`, not `"page": 1`).

| Old                                    | New                                                                    |
| -------------------------------------- | ---------------------------------------------------------------------- |
| `periodType: int 0–7`                  | `periodType: string` (`last_7d` / `last_30d` / `this_month` / `last_month` / `today` / `this_week` / `total` — default) |
| `periodStart` / `periodEnd: YYYY-MM-DD`| `begin` / `end: Unix milliseconds string`                              |
| `pageSize: int (max 50)`               | `limit: string` (schema says max 100; **practical max is 95** — see FAQ) |
| `orderItem: int 1/3/5/6/7`             | `orderBy: string` (`cTime` / `depAmt` / `vol` / `fee` / `rebate`)       |
| `orderType: int 1/2`                   | `orderDir: string` (`asc` / `desc`)                                     |
| `type: int 0/1/2/3`                    | `commissionCategory: string` (`SPOT` / `DERIVATIVE` / `BSC`)             |
| `kycVerifiedStatus: int 1/2`           | `kycStatus: string` (`unverified` / `verified`)                          |
| `status: int 0/1`                      | `linkStatus: string` (`normal` / `abnormal`)                             |
| `channelType: int 1/2`                 | `linkType: string` (`standard` / `co_inviter`)                           |
| `searchWord`                           | `keyword`                                                                |
| `descendantAffiliateId: int`           | `subAffiliateUid: string`                                                |

### Removed parameters

- `pageType` (was buggy — value `2` returned 400)
- `inviteeSource`
- `hasDeposit`, `hasTrade`, `countryCode`, `channelName` (from invitee-list — filter
  client-side now)
- `periodType`, `type` (from sub-affiliate-list — lifetime data only)
- `searchWord`, `orderType` (from co-inviter-list)

### Response shape changes

- Spot / Derivative / BSC breakdown is now a `details[]` array with
  `commissionCategory: SPOT|DERIVATIVE|BSC`. The old top-level
  `commissionDer`/`commissionSpot`/`commissionBsc` fields are gone.
- **No top-level `commission` total** — sum across `details[]`.
- **No `total` count** in list responses — paginate until you get an empty `data` array.
- Field renames in responses:

| Old                  | New                |
| -------------------- | ------------------ |
| `deposit`            | `depAmt`           |
| `volume`             | `vol`              |
| `traders`            | `traderCnt`        |
| `firstTimeTrader`    | `firstTraderCnt`   |
| `invitees`           | `inviteeCnt`       |
| `lastUpdatedTime`    | `uTime`            |
| `withdrawalAmount`   | `wdAmt`            |
| `relateTime`         | `joinTime`         |
| `firstTimeTraded`    | `firstTradeTime`   |
| `kycVerifiedTime`    | `kycTime`          |
| `kycCountry`         | `country`          |
| `feeTierLevelName`   | `feeTierRank`      |
| `rebateRatio`        | `rebateRate`       |
| `totalReward`        | `totalCommission`  |
| `totalTradingVolume` | `totalVol`         |
| `fees`               | `totalFee`         |

### New fields

`okx-affiliate-link-list`:

- `commission24h` — rolling 24-hour commission per link
- `joinLink` — full invite URL
- `coInviterCommissionRate` / `inviteeDiscountRate` — commission breakdown made explicit

### Known issues (added to FAQ)

- `okx-affiliate-invitee-list` returns `500 system error` when `limit ≥ 99`. Cap at `"95"`.
- `okx-affiliate-link-list` and `okx-affiliate-co-inviter-list` silently accept invalid
  `linkType` / `linkStatus` values and return all rows.
- `okx-affiliate-invitee-detail` returns the same `code: 51621 "The user isn't your invitee"`
  for both legitimately not-yours UIDs and malformed UIDs.

---

## 2026-05-07 — bundle OpenClaw skill in-tree

- Move the OpenClaw skill content into `skills/openclaw-affiliate-mcp/` (mirroring the
  `okx/agent-skills` layout).
- Add `skills/README.md` as a skill-pack index.
- Convert `README.zh-CN.md` from Traditional to Simplified Chinese (mainland-style).

## 2026-05-07 — initial release

- README (English + 中文) with quick-start matrix per client
- `INSTALL.md` decision tree for AI agents
- Per-client install guides: Claude Code, Codex, Hermes, Cursor, OpenClaw, generic
- Tools reference
- `periodType` quick reference
- Usage examples
- FAQ
