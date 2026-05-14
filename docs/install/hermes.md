# Install on Hermes Agent

[← Back to install index](../../README.md#quick-start)

Hermes Agent's `native-mcp` client supports remote HTTP MCP servers with static
`Authorization` headers, but it does **not** run an OAuth flow on its own. Two of OKX's
OAuth quirks make a one-click install impossible without help:

1. The **mandatory `resource` parameter** ([RFC 8707](https://datatracker.ietf.org/doc/html/rfc8707))
   on every authorize and token request.
2. The **non-discovery DCR (Dynamic Client Registration) endpoint** at
   `/api/v5/mcp/auth/register`.

Until Hermes' MCP client picks up RFC 8707 + custom DCR, Hermes users install via the
**bundled skill** in this repo at
[`skills/hermes-affiliate-mcp/`](../../skills/hermes-affiliate-mcp/). The skill performs the
OAuth dance with stdlib-only Python, then writes the bearer token directly into
`~/.hermes/config.yaml` so Hermes' hot-reload picks it up within seconds — no restart.

## What the skill provides

- [`SKILL.md`](../../skills/hermes-affiliate-mcp/SKILL.md) — agent-readable decision tree
- [`scripts/register.py`](../../skills/hermes-affiliate-mcp/scripts/register.py) — DCR (one-time per install)
- [`scripts/auth.py`](../../skills/hermes-affiliate-mcp/scripts/auth.py) — build authorize URL + PKCE
- [`scripts/exchange.py`](../../skills/hermes-affiliate-mcp/scripts/exchange.py) — exchange code for tokens
- [`scripts/refresh.py`](../../skills/hermes-affiliate-mcp/scripts/refresh.py) — refresh access token
- [`scripts/write_config.py`](../../skills/hermes-affiliate-mcp/scripts/write_config.py) — inject bearer into `~/.hermes/config.yaml`
- [`scripts/auto_refresh.py`](../../skills/hermes-affiliate-mcp/scripts/auto_refresh.py) — refresh + rewrite config in one shot (cron entry point)
- [`scripts/status.py`](../../skills/hermes-affiliate-mcp/scripts/status.py) — 1-line install state summary
- [`reference/`](../../skills/hermes-affiliate-mcp/reference/) — endpoint specs, known issues, tool overview, callback-page tips

All scripts are stdlib-only — no `pip install` required.

## Install

### Option A — full repo clone (simplest)

```bash
git clone https://github.com/okx/growth-affiliate-tool /tmp/growth-affiliate-tool
cp -r /tmp/growth-affiliate-tool/skills/hermes-affiliate-mcp \
      ~/.hermes/skills/okx-affiliate-mcp
```

### Option B — sparse checkout (only the skill)

```bash
git clone --filter=blob:none --sparse \
  https://github.com/okx/growth-affiliate-tool /tmp/growth-affiliate-tool
cd /tmp/growth-affiliate-tool && git sparse-checkout set skills/hermes-affiliate-mcp
cp -r skills/hermes-affiliate-mcp ~/.hermes/skills/okx-affiliate-mcp
```

Either way, ask your Hermes agent:

> *Install the OKX Affiliate MCP.*

The agent loads `SKILL.md`, runs `register.py` → `auth.py` → `exchange.py` →
`write_config.py`, and walks you through the OAuth flow. End-to-end takes ~2 minutes.

## What to expect during OAuth

The skill produces a regular OKX OAuth URL. After you click *Authorize* on OKX:

- ⚠️ Your browser will land on a **blank / "site can't be reached" page** at
  `localhost:8787/callback?...`. **This is expected.** OKX has finished its work — there is
  no local server running on your machine; we just need the URL.
- **Copy the entire URL from your browser's address bar** and paste it back into chat.
- The agent extracts the `code` parameter, calls `exchange.py`, and you are connected.

Full instructions for handling the callback page live in
[`skills/hermes-affiliate-mcp/SKILL.md`](../../skills/hermes-affiliate-mcp/SKILL.md) and
[`skills/hermes-affiliate-mcp/reference/blank-callback-page.md`](../../skills/hermes-affiliate-mcp/reference/blank-callback-page.md).

## Token lifecycle

After Step 3 (`exchange.py`), the skill writes:

- `~/.hermes/data/okx-affiliate-mcp/token.json` — `access_token` + `refresh_token` + `obtained_at`
- A managed block in `~/.hermes/config.yaml` containing the `mcp_servers.okx_affiliate`
  entry with the current bearer header

The `access_token` lifetime is ~1 hour. Two ways to keep Hermes seeing a fresh token:

- **Automatic (cron, recommended)** — schedule `scripts/auto_refresh.py` every 50 minutes,
  either via Hermes' built-in `cronjob` tool or your system crontab. See
  [`SKILL.md`](../../skills/hermes-affiliate-mcp/SKILL.md#automatic-refresh-cron) for
  snippets.
- **On-demand (LLM-driven)** — when a `mcp_okx_affiliate_*` call returns 401, the skill
  runs `auto_refresh.py` and retries.

Hermes hot-reloads `mcp_servers` on `config.yaml` change, so a token refresh becomes
visible within ~3 seconds without restarting the session.

## When Hermes' MCP client supports custom OAuth

The skill becomes unnecessary the day Hermes' `native-mcp` client handles the `resource`
parameter and the custom DCR endpoint. At that point the install path collapses to the
standard `mcp_servers` entry in `config.yaml` with no skill involved. We will update this
guide when that happens.

## Troubleshooting

| Symptom                                              | Fix                                                      |
| ---------------------------------------------------- | -------------------------------------------------------- |
| `invalid_grant: resource does not match`             | The skill missed adding the `resource` param — re-run `auth.py` and `exchange.py` from a clean state |
| Browser shows blank page after Authorize             | **Expected.** Copy the URL from the address bar         |
| `auto_refresh.py` / `refresh.py` returns 4xx         | Refresh token is dead. Re-run `auth.py` + `exchange.py` + `write_config.py` (skip `register.py`, `client.json` is still valid) |
| MCP calls return 401 right after refresh             | Hermes may have cached the old header; wait ~5 seconds for hot-reload, or call the tool again |
| `write_config.py` refuses to write (duplicate `mcp_servers`) | You already have a top-level `mcp_servers:` block outside the managed region. Comment it out, re-run `write_config.py`, then re-add your other servers inside the managed region |
| `403 Cloudflare Error 1010` on every MCP call (token is valid) | Your HTTP caller is using a non-browser User-Agent (`Python-urllib`, `curl`, …). Send a Chrome UA on the MCP request. See [`reference/known-issues.md`](../../skills/hermes-affiliate-mcp/reference/known-issues.md) |

For deeper debugging see
[`skills/hermes-affiliate-mcp/reference/known-issues.md`](../../skills/hermes-affiliate-mcp/reference/known-issues.md).
