---
name: okx-affiliate-mcp
description: "Install and maintain the OKX Affiliate MCP (OAuth) on Hermes Agent."
version: 1.0.0
author: Community
license: MIT
metadata:
  hermes:
    tags: [MCP, OAuth, OKX, Affiliate, Integrations]
    related_skills: [native-mcp]
---

# OKX Affiliate MCP for Hermes Agent

Install, authorize, and keep alive the OKX Growth Affiliate MCP
(`https://www.okx.com/api/v1/mcp/growth-affiliate-mcp`) on Hermes Agent.

After install, Hermes exposes 6 tools (named `mcp_okx_affiliate_*`):

- `okx-affiliate-performance-summary`
- `okx-affiliate-invitee-list`
- `okx-affiliate-invitee-detail`
- `okx-affiliate-link-list`
- `okx-affiliate-sub-affiliate-list`
- `okx-affiliate-co-inviter-list`

See `reference/tools-overview.md` for what each one returns.

## When to use this skill

Load this skill when the user asks to:

- "Install / set up / connect OKX Affiliate MCP on Hermes"
- "Refresh / renew the OKX Affiliate token"
- "Fix `401 Unauthorized` from `mcp_okx_affiliate_*` tools"
- "Set up cron / automatic refresh for the OKX Affiliate MCP"

## Why a skill (not a native MCP entry)

The OKX MCP is a remote HTTP MCP with two OAuth quirks that no MCP client
currently handles out of the box:

1. **Mandatory `resource` parameter** (RFC 8707) on every authorize and token
   request — omitting it returns `invalid_grant: resource does not match`.
2. **Non-discovery Dynamic Client Registration** endpoint at
   `/api/v5/mcp/auth/register` — not advertised by `.well-known`.

Hermes Agent's `native-mcp` client supports static HTTP headers but does not
run an OAuth flow. This skill runs the flow with four small stdlib-only
Python scripts (adapted from the upstream
[`okx/growth-affiliate-tool`](https://github.com/okx/growth-affiliate-tool)
repo) and writes the resulting bearer token straight into
`~/.hermes/config.yaml`. Hermes hot-reloads `mcp_servers` on config change,
so the MCP appears within seconds — no restart needed.

## State files

All credentials live under `~/.hermes/data/okx-affiliate-mcp/` (gitignored):

| File           | Content                                                   | Written by    |
|----------------|-----------------------------------------------------------|---------------|
| `client.json`  | DCR-registered client (`client_id`, `redirect_uris`, …)   | register.py   |
| `pkce.json`    | `code_verifier`, `code_challenge`, `state` for this auth  | auth.py       |
| `auth_url.txt` | URL the user must open in a browser                       | auth.py       |
| `token.json`   | `access_token`, `refresh_token`, `expires_in`, `obtained_at` | exchange.py / refresh.py |

The bearer token in `token.json` is also mirrored into `~/.hermes/config.yaml`
inside a managed block delimited by:

```
# >>> okx-affiliate-mcp managed block — do not edit by hand >>>
... mcp_servers entry ...
# <<< okx-affiliate-mcp managed block <<<
```

`write_config.py` only touches text between those two markers; everything
else in `config.yaml` is preserved byte-for-byte.

## Decision tree

When invoked, always start by running:

```bash
python3 SKILL_DIR/scripts/status.py
```

Branch on the printed `state:`

```
state: ok                       → already installed and token valid; you are done
state: expiring_soon | expired  → run scripts/auto_refresh.py (one shot)
state: not_installed            → Fresh install (steps 1–4)
state: registered_but_unauthed  → resume from Step 2 (auth.py)
state: token_malformed          → resume from Step 2 (auth.py)
```

## Fresh install (4 steps)

> Replace `SKILL_DIR` with the absolute path to this skill's directory
> (the directory containing `SKILL.md`).

### Step 1 — Register a DCR client (one-time)

```bash
python3 SKILL_DIR/scripts/register.py
```

Writes `client.json`. Idempotent — safe to re-run.

### Step 2 — Generate authorize URL

```bash
python3 SKILL_DIR/scripts/auth.py
```

Prints the URL and saves it to `auth_url.txt`. Send the URL to the user.

**⚠ Before the user clicks Authorize, tell them — explicitly, in plain
language — what to expect:**

> After clicking Authorize, your browser will try to load
> `http://localhost:8787/callback...` and you'll see a **blank / "site can't
> be reached" page**. That blank page **is** the success state. Do not
> reload or close the tab. Just **copy the entire URL from the browser's
> address bar** (it contains `code=...&state=...`) and paste it back.

On the consent page they should only enable **Live Trading → Read-only**.
Everything else off. See `reference/blank-callback-page.md` for the full
walkthrough.

### Step 3 — Exchange code for token

```bash
python3 SKILL_DIR/scripts/exchange.py "<callback-url-or-code>"
```

Accepts either the bare `code` value or the full callback URL. Verifies
`state` against `pkce.json`, exchanges the code, writes `token.json`.

### Step 4 — Inject token into Hermes config

```bash
python3 SKILL_DIR/scripts/write_config.py
```

Adds (or replaces) the managed `mcp_servers.okx_affiliate` block in
`~/.hermes/config.yaml`. Hermes will hot-reload within ~3 seconds.

#### If config.yaml already has a top-level `mcp_servers:` key

YAML disallows two top-level `mcp_servers:` keys. `write_config.py` will
bail with a clear error. Either:

- merge our entry under the existing block manually (copy the snippet it
  prints), or
- comment out the existing block before re-running write_config.py and
  re-add your other servers inside the managed region.

### Step 5 — Verify

Ask Hermes to call the MCP:

```
Show me my affiliate performance summary.
```

Hermes should call `mcp_okx_affiliate_okx_affiliate_performance_summary`
and return a numeric payload. If you see `401 Unauthorized`, run
`scripts/auto_refresh.py` and retry.

## Refresh (existing install)

```bash
python3 SKILL_DIR/scripts/auto_refresh.py
```

This is `refresh.py + write_config.py` in one shot:

1. POSTs `grant_type=refresh_token` to OKX (with the mandatory `resource`
   parameter).
2. Overwrites `token.json` with the new access_token + refresh_token +
   `obtained_at`.
3. Rewrites the managed block in `~/.hermes/config.yaml`.
4. Hermes hot-reloads the MCP within seconds.

If `refresh.py` fails (`refresh_token` is dead), fall back to a fresh login
— `auth.py` → `exchange.py` → `write_config.py`. `client.json` is still
valid, so you can skip `register.py`.

## Automatic refresh (cron)

`access_token` lives ~1 hour. To keep it valid without LLM involvement,
register a cron job that runs `auto_refresh.py` every 50 minutes. Two
options:

### Option A — Hermes built-in cron (recommended)

Use the `cronjob` tool inside Hermes:

```
schedule: "*/50 * * * *"
prompt:   "Run: python3 ~/.hermes/skills/<category>/okx-affiliate-mcp/scripts/auto_refresh.py"
```

(Replace `<category>` with wherever the skill is installed. If you cloned
this repo into `~/.hermes/skills/okx-affiliate-mcp/`, no category prefix
needed.)

### Option B — system crontab

```cron
*/50 * * * * /usr/bin/python3 /home/USER/.hermes/skills/okx-affiliate-mcp/scripts/auto_refresh.py >/dev/null 2>&1
```

Either option keeps `config.yaml`'s bearer token always fresh; the agent
never sees a 401.

## On-demand refresh (no cron)

If you skip cron, the LLM can recover from a 401 the OpenClaw way: when
any `mcp_okx_affiliate_*` tool returns 401 / "token expired", load this
skill and run `scripts/auto_refresh.py`, then retry the original call.
Hermes hot-reloads MCP within a few seconds; if the retry still 401s,
sleep ~3 seconds and try once more.

## Critical pitfalls (read before debugging)

- **`resource` parameter** — required on **both** the authorize request
  *and* the token request, *and* the refresh request. `invalid_grant:
  resource does not match` always means this is missing.
- **DCR endpoint** is `/api/v5/mcp/auth/register`, not the discovery default.
- **Token endpoint** is `/api/v5/mcp/auth/token`.
- **Authorize page** needs the `flow=code` query param — without it OKX
  may serve a different UI.
- **User-Agent** — OKX is behind Cloudflare; `Python-urllib/3.x` gets a
  403 `error code: 1010`. Scripts already send a browser-ish UA.
- **Scope** — keep `live:read` unless the user has a real need; broader
  scopes alarm the user on the consent screen and are not used by this MCP.
- **Config YAML duplicate key** — if there's a top-level `mcp_servers:`
  block outside our managed region, `write_config.py` will refuse to write
  (see Step 4 above).

See `reference/oauth-endpoints.md` and `reference/known-issues.md` for full
specs and historical bugs.

## Uninstall

```bash
rm -rf ~/.hermes/data/okx-affiliate-mcp
# Then delete the managed block between BLOCK_BEGIN/BLOCK_END markers in
# ~/.hermes/config.yaml. Hermes will hot-reload and drop the MCP.
```

To also revoke OAuth access, sign in to OKX → *Connected apps* and remove
the entry there.

## Credits

OAuth scripts adapted from
[`okx/growth-affiliate-tool`](https://github.com/okx/growth-affiliate-tool)
(MIT). Hermes-specific glue (status, write_config, auto_refresh) added for
this skill.
