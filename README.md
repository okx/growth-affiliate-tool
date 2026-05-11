# OKX Growth Affiliate Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](README.md) | [中文](README.zh-CN.md)

A remote MCP (Model Context Protocol) endpoint that lets AI agents query the OKX Affiliate
portal — performance, invitees, links, sub-affiliates — through natural language, with no
manual API plumbing.

> **Endpoint:** `https://www.okx.com/api/v1/mcp/growth-affiliate-mcp`
> **Transport:** Streamable HTTP
> **Auth:** OAuth 2.0 (per-user, hosted by OKX)

## What you can do once it is connected

Ask your agent things like:
- *"Show me my affiliate performance for the last 30 days."*
- *"Who are my top 10 invitees this quarter by commission?"*
- *"List all my invite links sorted by trader count."*
- *"How is sub-affiliate `XYZ` performing this month?"*

The agent picks the right tool, runs it, and answers in natural language.

## Quick start

Pick the row that matches your client. Each guide is a single command plus a 4-step OAuth flow.

| Client                          | Native MCP OAuth | Install guide                                                |
| ------------------------------- | :--------------: | ------------------------------------------------------------ |
| **Claude Code** (CLI)           | ✅               | [`docs/install/claude-code.md`](docs/install/claude-code.md) |
| **Codex CLI**                   | ✅               | [`docs/install/codex.md`](docs/install/codex.md)             |
| **Hermes**                      | ✅               | [`docs/install/hermes.md`](docs/install/hermes.md)           |
| **Cursor**                      | ✅               | [`docs/install/cursor.md`](docs/install/cursor.md)           |
| **Generic MCP client**          | ✅               | [`docs/install/generic.md`](docs/install/generic.md)         |
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

## Prerequisites

- An **OKX account** that is enrolled as an Affiliate
- A **client** in the table above (or any other MCP-compliant agent)
- A browser to complete the one-time OAuth handshake

That is it — there is no SDK to install and no local server to run. The MCP is hosted by OKX.

## License

[MIT](LICENSE).

## Contact

Issues and feature requests: please open a GitHub issue on this repo.
