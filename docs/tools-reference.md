# Tools reference

Six MCP tools, all read-only. Every tool that takes a time period uses the same
[`periodType` codes](period-type.md).

| #  | Tool                                                              | Purpose                          |
| -- | ----------------------------------------------------------------- | -------------------------------- |
| 1  | [`okx-affiliate-performance-summary`](#1-performance-summary)     | Aggregate metrics                |
| 2  | [`okx-affiliate-invitee-list`](#2-invitee-list)                   | Paginated invitee list           |
| 3  | [`okx-affiliate-invitee-detail`](#3-invitee-detail)               | Single invitee deep dive          |
| 4  | [`okx-affiliate-link-list`](#4-link-list)                         | Your invite links                |
| 5  | [`okx-affiliate-sub-affiliate-list`](#5-sub-affiliate-list)       | Sub-affiliates in MLRS network   |
| 6  | [`okx-affiliate-co-inviter-list`](#6-co-inviter-list)             | Channels where you co-invite     |

> **Naming note:** All numeric values in the schema (page, limit, periodType, etc.) are passed
> as **strings**, not integers. Pass `"1"`, not `1`.

---

## 1. Performance summary

**Tool name:** `okx-affiliate-performance-summary`

Aggregate performance for the connected affiliate over a chosen time window.

### Parameters

| Param        | Type   | Required | Default  | Description                                                                       |
| ------------ | ------ | :------: | :------: | --------------------------------------------------------------------------------- |
| `periodType` | string | No       | `total`  | Time window — see [`period-type.md`](period-type.md). Omit for custom range.       |
| `begin`      | string | When custom | —      | Custom-range start, **Unix milliseconds**, inclusive. Required with `end`.         |
| `end`        | string | When custom | —      | Custom-range end, **Unix milliseconds**, inclusive. Required with `begin`.         |

> Pass `begin` and `end` for a custom range and omit `periodType` (or set any non-listed
> string). The server treats unknown `periodType` values as "use the supplied date range".

### Return shape

```json
{
  "msg": "",
  "code": "0",
  "data": [{
    "depAmt": "37337746.56",
    "inviteeCnt": "1885",
    "uTime": "1778222037000",
    "details": [
      {"commissionCategory": "SPOT",       "commission": "27327.74", "vol": "174375947.61", "traderCnt": "574", "firstTraderCnt": "574"},
      {"commissionCategory": "DERIVATIVE", "commission": "497463.39", "vol": "...",         "traderCnt": "785", "firstTraderCnt": "785"},
      {"commissionCategory": "BSC",        "commission": "4.18",      "vol": "1305.16",     "traderCnt": "2",   "firstTraderCnt": "2"}
    ]
  }]
}
```

### Field map (response)

| Field                            | Meaning                                                       |
| -------------------------------- | ------------------------------------------------------------- |
| `depAmt`                         | Total deposits in window                                      |
| `inviteeCnt`                     | Invitee count                                                 |
| `uTime`                          | Server snapshot time, Unix ms                                  |
| `details[]`                      | Per-category breakdown (SPOT / DERIVATIVE / BSC)              |
| `details[].commissionCategory`   | `"SPOT"` / `"DERIVATIVE"` / `"BSC"`                            |
| `details[].commission`           | Commission earned in that category                             |
| `details[].vol`                  | Trading volume in that category                                |
| `details[].traderCnt`            | Active traders in that category                                |
| `details[].firstTraderCnt`       | First-time traders in that category                            |

> **No top-level `commission` total** — sum across `details[]` to get the grand total.

---

## 2. Invitee list

**Tool name:** `okx-affiliate-invitee-list`

Paginated list of your direct invitees with their trading, deposit, and KYC stats.

### Parameters

| Param                | Type   | Required | Default | Description                                                                                  |
| -------------------- | ------ | :------: | :-----: | -------------------------------------------------------------------------------------------- |
| `page`               | string | No       | `"1"`   | Page number (starts at 1). Non-numeric values fall back to `"1"`.                            |
| `limit`              | string | No       | `"10"`  | Items per page. **Practical max is `"95"`** — see [FAQ](faq.md) on the `limit ≥ 99 → 500` bug. |
| `periodType`         | string | No       | `total` | Time window for stat fields                                                                   |
| `begin`              | string | When custom | —    | Custom-range start, Unix ms                                                                   |
| `end`                | string | When custom | —    | Custom-range end, Unix ms                                                                     |
| `commissionCategory` | string | No       | —       | Filter by category — `SPOT` / `DERIVATIVE` / `BSC`                                            |
| `kycStatus`          | string | No       | —       | `verified` (KYC2+) / `unverified`                                                             |
| `keyword`            | string | No       | —       | Substring match on UID or channel name                                                       |
| `subAffiliateUid`    | string | No       | —       | Filter to invitees attributed to a specific sub-affiliate UID                                |
| `orderBy`            | string | No       | `cTime` | Sort field — `cTime` (join time) / `depAmt` / `vol` / `fee` / `rebate`                        |
| `orderDir`           | string | No       | `desc`  | Sort order — `asc` / `desc`                                                                   |

### Return shape (each row)

```json
{
  "uid": "...",
  "channelName": "CRYPTO1818",
  "country": "CN",
  "kycStatus": "verified",
  "kycTime": "1755440968000",
  "joinTime": "1755424349000",
  "firstTradeTime": "1755496800000",
  "feeTierRank": "6",
  "rebateRate": "0.2000",
  "isCompliant": true,
  "depAmt": "10329631.36",
  "totalCommission": "104146.07",
  "totalFee": "347153.57",
  "totalVol": "1186843492.29"
}
```

`depAmt`, `totalCommission`, `totalFee`, `totalVol` are **scoped to the requested
`periodType`**. To get lifetime totals, omit `periodType` (default is `total`).

> **No `total` count in the response** — keep paginating until you get an empty `data` array.
> See [FAQ](faq.md) for pagination strategy.

---

## 3. Invitee detail

**Tool name:** `okx-affiliate-invitee-detail`

Deep dive on a single invitee, by external UID.

### Parameters

| Param | Type   | Required | Description                                  |
| ----- | ------ | :------: | -------------------------------------------- |
| `uid` | string | ✅       | The invitee's external UID (from list above) |

### Return fields

```json
{
  "uid": "743072917935893796",
  "affiliateCode": "CRYPTO1818",
  "region": "China",
  "level": "Lv1",
  "inviteeLevel": "2",
  "inviteeRebateRate": "0.2",
  "joinTime": "1755424349000",
  "kycTime": "1755440968744",
  "firstTradeTime": "1755496800000",
  "depAmt": "10329631.35",
  "wdAmt": "9795977.54",
  "totalVol": "1186843492.29",
  "totalCommission": "104146.07",
  "accFee": "347153.56",
  "volMonth": "37.04"
}
```

`volMonth` is the calendar-month-to-date trading volume — useful for spotting users whose
activity dropped this month even though their lifetime numbers look healthy.

> ⚠️ Passing a UID that does not exist or is not your invitee returns
> `code: 51621, msg: "The user isn't your invitee"` rather than a 404 — see
> [FAQ](faq.md#q-invitee-detail-returns-the-user-isnt-your-invitee).

---

## 4. Link list

**Tool name:** `okx-affiliate-link-list`

Your invite links with cumulative invitee count, trader count, and commission.

### Parameters

| Param        | Type   | Required | Default  | Description                                                  |
| ------------ | ------ | :------: | :------: | ------------------------------------------------------------ |
| `page`       | string | No       | `"1"`    | Page number                                                   |
| `limit`      | string | No       | `"10"`   | Items per page; max `"95"` in practice                       |
| `linkType`   | string | No       | —        | `standard` (your own invite links) / `co_inviter` (links you co-invite on) |
| `linkStatus` | string | No       | —        | `normal` / `abnormal`                                         |

> ⚠️ **Invalid `linkType` / `linkStatus` values are silently accepted** and the filter is
> dropped (you get all rows back). Always check returned `linkType` / `linkStatus` matches
> what you asked for. See [FAQ](faq.md#q-i-passed-linktypewhatever-and-still-got-all-results).

### Return fields (per link)

```json
{
  "channelId": "49323294",
  "channelName": "CRYPTO1818",
  "joinLink": "https://okx.com/join/CRYPTO1818",
  "linkType": "standard",
  "linkStatus": "normal",
  "isDefault": true,
  "cTime": "1705316204000",
  "inviterCommissionRate": "0.3000",
  "coInviterCommissionRate": "0.0000",
  "inviteeDiscountRate": "0.2000",
  "inviteeCnt": "1850",
  "traderCnt": "830",
  "totalCommission": "524194.29",
  "commission24h": "173.09"
}
```

`commission24h` is the rolling 24-hour commission for that specific link — handy for spotting
which channels are hot right now.

---

## 5. Sub-affiliate list

**Tool name:** `okx-affiliate-sub-affiliate-list`

Sub-affiliates in your MLRS (multi-level referral system) network. **Lifetime data only** —
the new schema removed the per-period filter.

### Parameters

| Param                | Type   | Required | Default | Description                                                          |
| -------------------- | ------ | :------: | :-----: | -------------------------------------------------------------------- |
| `page`               | string | No       | `"1"`   | Page number                                                          |
| `limit`              | string | No       | `"10"`  | Items per page; max `"95"` in practice                                |
| `commissionCategory` | string | No       | —       | `SPOT` / `DERIVATIVE` / `BSC`                                         |
| `keyword`            | string | No       | —       | Search by sub-affiliate UID                                           |
| `orderBy`            | string | No       | (joinTime newest first) | `cTime` / `depAmt` / `vol` / `fee` / `rebate`         |
| `orderDir`           | string | No       | `desc`  | `asc` / `desc`                                                        |

### Return fields (per row)

Sub-affiliate UID, invitee count, trader count, trading volume, fees, commission. Lifetime
only.

---

## 6. Co-inviter list

**Tool name:** `okx-affiliate-co-inviter-list`

Channels where you are listed as a co-inviter (i.e. you share commission on those links).

### Parameters

| Param        | Type   | Required | Default | Description                          |
| ------------ | ------ | :------: | :-----: | ------------------------------------ |
| `page`       | string | No       | `"1"`   | Page number                          |
| `limit`      | string | No       | `"10"`  | Items per page; max `"95"` in practice |
| `linkStatus` | string | No       | —       | `normal` / `abnormal`                 |

### Return fields (per row)

Channel name, your commission share, partner / co-inviter UIDs, invitee stats, channel
status. The schema is rich (~22 fields per row).

---

## Notes shared across all tools

- **All numeric inputs are passed as strings.** `page`, `limit`, `begin`, `end` — all
  strings.
- **Numeric outputs are decimal strings** — preserve precision when parsing (parse as
  `Decimal` / `BigDecimal`).
- **Timestamps are Unix epoch milliseconds** — `joinTime`, `firstTradeTime`, `kycTime`,
  `uTime`, `cTime`.
- **Token lifetime is approximately 1 hour.** Most clients refresh transparently; if you see
  401s, trigger your client's MCP reconnect / refresh.
- **Rate limit:** the endpoint returns `429 Too Many Requests` (`code: 50011`) for bursty
  traffic. Aim for ≤ 5 RPS; back off on 429.
- **`limit` cap:** schema says max 100 but anything ≥ 99 currently returns `500 system
  error`. Use `≤ 95` to be safe.
