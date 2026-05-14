# OKX Growth Affiliate Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](README.md) | [中文](README.zh-CN.md)

A remote MCP (Model Context Protocol) endpoint that lets AI agents query the OKX Affiliate
portal — performance, invitees, links, sub-affiliates — through natural language, with no
manual API plumbing.

<p align="center">
  <img src="docs/videos/affiliate-mcp-promo.gif" alt="60-second affiliate MCP promo" width="720"/>
</p>

> **Endpoint:** `https://www.okx.com/api/v1/mcp/growth-affiliate-mcp`
> **Transport:** Streamable HTTP
> **Auth:** OAuth 2.0 (per-user, hosted by OKX)

## What it looks like

Ask in natural language. The agent picks the right tool and answers — examples below
(UIDs and figures are illustrative).

```
You    ❯ Yesterday's report.

Agent  ❯ 📊 Commission $350 (-30% vs 7d avg). Volume $3.5M. 6 new invitees.
         Top 3:  UID …A1B2  $91  VIP2
                 UID …C3D4  $50  VIP1
                 UID …E5F6  $28  Regular  ← qualifies for VIP1
         ⚠️ 3 users deposited $1.8K total, didn't trade. Rescue today.
```

```
You    ❯ Who should I reach out to?

Agent  ❯ 🎯 33 candidates, 4 tiers:
         🔥 Star activators (joined <7d, already producing):    UID …N1P2, …Q3R4
         🐋 Regular users doing whale volume → push VIP1:        UID …S5T6, …U7V8, …W9X0
         ⚠️ Big bag-sitters (deposited, didn't trade):           UID …Y1Z2 ($10K idle 8d)
         🆕 KYC done, no deposit yet:                            13 users this week
```

```
You    ❯ Which whales are slipping?

Agent  ❯ ⚠️ Lifetime top 50 → only 23 still active.
         🔴 Cashed out:  UID …K1L2 ($104K LTV, withdrew 95% of $10M)
         🟡 Parked:      UID …M3N4 ($26K LTV, kept 94% on platform) ← easiest win
         🟠 Decaying:    UID …P5Q6 ($18K LTV, 30d volume = 0)
         Combined LTV at risk: $208K (~46% of node's 12-month commission).
```

## Quick start

Pick the row that matches your client. Each guide is a single command plus a 4-step OAuth flow.

| Client                          | Native MCP OAuth | Install guide                                                |
| ------------------------------- | :--------------: | ------------------------------------------------------------ |
| **Claude Code** (CLI)           | ✅               | [`docs/install/claude-code.md`](docs/install/claude-code.md) |
| **Codex CLI**                   | ✅               | [`docs/install/codex.md`](docs/install/codex.md)             |
| **OpenClaw**                    | ❌ (use skill)   | [`docs/install/openclaw.md`](docs/install/openclaw.md)       |

> **OpenClaw note:** OpenClaw's built-in MCP runtime does not yet handle OKX's non-standard
> OAuth requirements (mandatory `resource` parameter and a non-discovery DCR endpoint). Until
> upstream support lands, OpenClaw users install via the bundled skill at
> [`skills/openclaw-affiliate-mcp/`](skills/openclaw-affiliate-mcp/) — a drop-in skill pack
> that walks the agent through the OAuth flow.

## Authorization scopes

When you connect, OKX will ask which scopes to grant. **For this MCP only the read paths are
needed**, so the recommended default is just **Live Trading → Read-only**:

| Scope               | Recommended | What it unlocks                                       |
| ------------------- | :---------: | ----------------------------------------------------- |
| `live:read`         | ✅          | All read tools below (performance, invitees, links…)  |
| `live:trade`        | ❌          | Place / modify / cancel orders — not used by this MCP |
| `live:earn`         | ❌          | Earn product subscriptions — not used by this MCP     |
| `live:asset_transfer` | ❌        | Transfer assets — not used by this MCP                |
| `demo:*`            | ❌          | Demo trading — not used by this MCP                   |

You can always re-run `/mcp` (or your agent's equivalent) to widen scopes later.

## Tools at a glance

| #  | Tool                                  | Purpose                                              |
| -- | ------------------------------------- | ---------------------------------------------------- |
| 1  | `okx-affiliate-performance-summary`   | Aggregate metrics — invitees, deposits, volume, commission, broken down by Spot / Derivatives / BSC |
| 2  | `okx-affiliate-invitee-list`          | Paginated invitee list with deposits, trading, KYC   |
| 3  | `okx-affiliate-invitee-detail`        | Deep dive on a single invitee by external UID         |
| 4  | `okx-affiliate-link-list`             | Your invite links + commission rates + cumulative stats (incl. 24h commission) |
| 5  | `okx-affiliate-sub-affiliate-list`    | Sub-affiliates in your MLRS network (lifetime data)  |
| 6  | `okx-affiliate-co-inviter-list`       | Channels where you are listed as a co-inviter        |

Full parameters and return fields → [`docs/tools-reference.md`](docs/tools-reference.md).

## Documentation

| Document                                                       | Description                                                  |
| -------------------------------------------------------------- | ------------------------------------------------------------ |
| [Tools reference](docs/tools-reference.md)                     | Every tool, every parameter, every return field              |
| [Usage examples](docs/usage-examples.md)                       | Natural-language prompts that route to each tool             |
| [`periodType` quick reference](docs/period-type.md)            | The eight time-window codes used across most tools           |
| [FAQ](docs/faq.md)                                             | Token expiry, 400 errors, scope mismatches, common pitfalls  |
| [Agent install bootstrap](INSTALL.md)                          | Decision tree an AI agent can read end-to-end                |
| [Skills index](skills/README.md)                               | Skills for runtimes that need custom OAuth handling          |
| [**Usage scenarios**](examples/README.md)                      | Drop-in skill packs for common analysis tasks (daily briefing, churn rescue, etc.) |

## Prerequisites

- An **OKX account** that is enrolled as an Affiliate
- A **client** in the table above (or any other MCP-compliant agent)
- A browser to complete the one-time OAuth handshake

That is it — there is no SDK to install and no local server to run. The MCP is hosted by OKX.

## License

[MIT](LICENSE).

## Contact

Issues and feature requests: please open a GitHub issue on this repo.
