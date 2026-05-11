# openclaw-affiliate-mcp (skill)

An OpenClaw skill that walks an agent through installing and maintaining OAuth credentials
for the [OKX Affiliate MCP](https://www.okx.com/api/v1/mcp/growth-affiliate-mcp).

> This skill ships as part of the
> [`zhqingliu-lab/growth-affiliate-tool`](https://github.com/zhqingliu-lab/growth-affiliate-tool)
> repository. For Claude Code, Codex, Hermes, Cursor, and other clients with native MCP
> OAuth, see the [parent repo's install guides](../../docs/install/) — those clients do not
> need this skill.

## Why this exists

OKX's OAuth server has two non-standard requirements:

1. A mandatory `resource` parameter on every authorize/token request
2. A non-discovery DCR endpoint at `/api/v5/mcp/auth/register`

Most agent runtimes (Codex, Claude Code, etc.) accept the MCP URL directly and handle the
OAuth dance natively. **OpenClaw's built-in mcporter does not yet handle these quirks**, so
we hand the whole flow to a skill: when the agent needs to install or refresh credentials,
it loads `SKILL.md` and follows the decision tree.

## Audience

The reader of `SKILL.md` is the **agent**, not a human. The agent invokes the scripts under
`scripts/`, talks to the user only when it needs the OAuth callback URL pasted back, and
writes credentials to `~/.openclaw/data/okx-affiliate-mcp/`.

## Install

From within the `growth-affiliate-tool` repo, drop this directory into your OpenClaw skills
path:

```bash
# Option A — clone the parent repo and symlink / copy the skill
git clone https://github.com/zhqingliu-lab/growth-affiliate-tool /tmp/growth-affiliate-tool
cp -r /tmp/growth-affiliate-tool/skills/openclaw-affiliate-mcp \
      ~/.openclaw/workspace/skills/okx-affiliate-mcp

# Option B — sparse checkout if you only want the skill
git clone --filter=blob:none --sparse \
  https://github.com/zhqingliu-lab/growth-affiliate-tool /tmp/growth-affiliate-tool
cd /tmp/growth-affiliate-tool && git sparse-checkout set skills/openclaw-affiliate-mcp
cp -r skills/openclaw-affiliate-mcp ~/.openclaw/workspace/skills/okx-affiliate-mcp
```

Then ask your OpenClaw agent:

> *Install the OKX Affiliate MCP.*

## Layout

```
SKILL.md                    # Agent-facing instructions + decision tree
scripts/
  _common.py                # Shared helpers (stdlib only)
  register.py               # DCR — one-time
  auth.py                   # Build authorize URL + PKCE
  exchange.py               # Code → tokens
  refresh.py                # Refresh access_token
reference/
  blank-callback-page.md    # The "blank page is the success signal" explainer
  oauth-endpoints.md        # All endpoints + payloads
  known-issues.md           # Real failures and fixes
  verify.md                 # How to sanity-check credentials
  openclaw-config.md        # Notes on wiring the token into OpenClaw
```

## Requirements

- Python 3.8+ (stdlib only — no `requests`, no `pip install` needed)
- An OKX account that is enrolled as an Affiliate

## Security

Credentials live under `~/.openclaw/data/okx-affiliate-mcp/`:

- `client.json` — public DCR record (no secret)
- `pkce.json` — short-lived per-attempt PKCE state
- `token.json` — access + refresh tokens

These never enter this repo. `.gitignore` enforces it.

## License

[MIT](../../LICENSE) — same as the parent repository.
