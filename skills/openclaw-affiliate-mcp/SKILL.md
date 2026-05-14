# okx-affiliate-mcp

Install and maintain OAuth credentials for the OKX Affiliate MCP on OpenClaw.

## When to use

Trigger this skill when the user asks to:
- "Install / set up / connect OKX Affiliate MCP" on OpenClaw
- Refresh / renew / fix OKX Affiliate MCP token
- Debug `invalid_grant` / `401` from OKX Affiliate MCP

Do **not** use this skill for other agents (Codex, Claude Code, etc.) — they handle the OAuth flow natively. This skill exists because OpenClaw's mcporter does not handle OKX's non-standard OAuth (custom token endpoint + required `resource` parameter).

## Background (1 minute read)

OKX Affiliate MCP is a **remote HTTP MCP** at `https://www.okx.com/api/v1/mcp/growth-affiliate-mcp`. There is no local server to run — clients call it over HTTP with `Authorization: Bearer <access_token>`.

Getting a token requires a four-step OAuth 2.0 flow with two OKX-specific quirks:

1. **Dynamic Client Registration (DCR)** — every install gets its own `client_id` from `/api/v5/mcp/auth/register`.
2. **`resource` parameter is mandatory** on both authorize and token requests. Omitting it produces `invalid_grant: resource does not match`.

The four steps:
1. **Register** a client (one-shot per install) → `client.json`
2. **Generate auth URL** (PKCE + state) → user opens it in a browser, logs into OKX, approves, gets redirected to `localhost:8787/callback?code=...`
3. **Exchange** the `code` for tokens → `token.json`
4. **Refresh** before the 1-hour `access_token` expires → updates `token.json`

## State files

All state lives in `~/.openclaw/data/okx-affiliate-mcp/` (cross-workspace, user-level credentials):

| File | Content | When written |
|---|---|---|
| `client.json` | DCR-registered client (`client_id`, `client_name`, `redirect_uris`, `scope`) | Step 1 |
| `pkce.json` | `code_verifier`, `code_challenge`, `state` for current auth attempt | Step 2 |
| `auth_url.txt` | The URL to send the user to | Step 2 |
| `token.json` | `access_token`, `refresh_token`, `expires_in`, `scope`, plus `obtained_at` (Unix sec) | Steps 3 & 4 |

Never commit any of these. They contain user credentials.

## Decision tree

When invoked, run this check first:

```
1. Does ~/.openclaw/data/okx-affiliate-mcp/token.json exist?
   - No  → go to Fresh install (all 4 steps)
   - Yes → check expiry: obtained_at + expires_in vs now
      - Expires in > 5 min  → tokens are fine, jump to "Verify" below
      - Expires soon / expired but refresh_token present → run refresh.py only
      - refresh_token also rejected → go to Fresh install
```

## Fresh install

Run scripts in order. Each script prints clear status and writes the next state file.

### Step 1 — Register a client (one-time)

```bash
python3 SKILL_DIR/scripts/register.py
```

This calls `POST https://www.okx.com/api/v5/mcp/auth/register` with a fixed redirect URI and scope, and writes `client.json`.

Skip if `client.json` already exists.

### Step 2 — Generate auth URL

```bash
python3 SKILL_DIR/scripts/auth.py
```

Prints the auth URL and writes `auth_url.txt` + `pkce.json`.

**Send the URL to the user** and walk them through what to expect.

#### What the user must do

1. Open the URL in a browser, signed in to the **OKX Affiliate account** they want to connect.
2. Click **Authorize** on the OKX consent page.
3. **The browser will jump to a blank / broken page.** This is the redirect to `http://localhost:8787/callback?...`.
4. **Copy the entire URL from the browser's address bar** and paste it back into chat.

#### ⚠️ The blank page is the success signal — emphasize this to the user

This is the single point where most users get stuck. Before sending the auth URL, and again right after, tell the user **explicitly and in plain language**:

> After you click Authorize, your browser will try to load `http://localhost:8787/callback...` and you'll see a **blank / white page** or an error like "This site can't be reached" / "connection refused" / "localhost refused to connect".
>
> **That blank page is exactly what we want — it means authorization worked.**
>
> Do **not** close the tab, do **not** click reload. Just **copy the full URL from the address bar** (it will look like `http://localhost:8787/callback?code=...&state=...`) and **paste it back to me**.
>
> The page being broken is normal because there is no server running on your computer at port 8787 — we just use that URL to receive the code from OKX.

State the blank-page expectation **before** they click Authorize, and again in the message asking for the URL. Users who do not hear this twice almost always panic and report the page as an error.

#### Common confusions and how to respond

- *"The page is blank / broken, did it fail?"* → No, that's the success state. Copy the address bar URL.
- *"I see localhost refused to connect."* → Same answer. The URL bar still has the `code`.
- *"There's no code on the page."* → The code is **in the URL bar**, not on the page itself. Ask them to copy from the address bar.
- *"Should I keep the tab open?"* → Yes until they've copied the URL. After that they can close it.
- *"It redirected back to OKX home / I don't see localhost in the URL."* → The auth attempt was canceled or expired. Re-run `auth.py` to get a fresh URL.

There is no local listener on port 8787. The redirect failing is **expected** and **required** — we only need the `code` and `state` from the URL bar.

### Step 3 — Exchange code for tokens

Once the user pastes the callback URL, extract `code` and pass it:

```bash
python3 SKILL_DIR/scripts/exchange.py "<code-from-callback-url>"
```

Verifies `state` against `pkce.json`, exchanges with `code_verifier` + `resource`, writes `token.json` (with `obtained_at` added).

### Step 4 — Verify

Hit a cheap MCP endpoint to confirm credentials work. See `reference/verify.md` for sample requests.

## Refresh (existing install)

```bash
python3 SKILL_DIR/scripts/refresh.py
```

Reads `token.json`, posts `grant_type=refresh_token` with `resource`, replaces `token.json`. If this returns 4xx, the refresh_token is dead — fall back to Fresh install (Steps 2–3 only; `client.json` is still valid).

## Wiring the token into OpenClaw

The skill stops at "you have a valid `token.json`". Configuring an HTTP MCP entry that reads `access_token` from this file is left to the OpenClaw config / agent runtime, not this skill. See `reference/openclaw-config.md` for current notes on this.

## Critical pitfalls (read before debugging)

- **`resource` parameter** — required on **both** the authorize request *and* the token request. If you get `invalid_grant: resource does not match`, this is almost always why.
- **DCR endpoint** is `/api/v5/mcp/auth/register`, not the discovery default.
- **Token endpoint** is `/api/v5/mcp/auth/token`, not the discovery-advertised one in some cases.
- **Authorize page** uses `flow=code` query param — without it, OKX may serve a different UI.
- **Scope** — DCR registers a base scope; the access token can be issued with a broader scope (`live:asset_transfer live:earn live:trade live:read`) at exchange time. Our default is `live:read` for safety.
- **Cloudflare WAF on the MCP endpoint** — actual tool calls go to `https://www.okx.com/api/v1/mcp/growth-affiliate-mcp`, which is fronted by Cloudflare and rejects non-browser User-Agents (`Python-urllib`, `curl`, …) with `403 Error 1010` *even when the token is valid*. Any custom HTTP caller (OpenClaw bridge, verify script, manual curl) **must** send a browser UA. See `reference/known-issues.md`.

See `reference/oauth-endpoints.md` and `reference/known-issues.md` for full details.

## Replacing SKILL_DIR

When invoking scripts, replace `SKILL_DIR` with the absolute path where the skill is installed (typically the directory containing this `SKILL.md`).
