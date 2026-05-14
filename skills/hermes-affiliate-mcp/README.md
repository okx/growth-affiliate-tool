# okx-affiliate-mcp (Hermes Agent skill)

A drop-in [Hermes Agent](https://hermes-agent.nousresearch.com) skill that installs the
[OKX Growth Affiliate MCP](https://github.com/okx/growth-affiliate-tool) — including
the OAuth 2.0 flow that Hermes' built-in MCP client cannot run on its own — and keeps
the bearer token fresh automatically.

After install, Hermes gains six new tools (`mcp_okx_affiliate_*`) that query the OKX
Affiliate portal in natural language: performance summary, invitees, links, sub-affiliates,
co-inviter network.

## Install

This skill ships inside the [`okx/growth-affiliate-tool`](https://github.com/okx/growth-affiliate-tool) repo. Drop it into your Hermes skills directory with either approach:

```bash
# Option A — full repo clone (simplest)
git clone https://github.com/okx/growth-affiliate-tool /tmp/growth-affiliate-tool
cp -r /tmp/growth-affiliate-tool/skills/hermes-affiliate-mcp \
      ~/.hermes/skills/okx-affiliate-mcp

# Option B — sparse checkout (only this skill)
git clone --filter=blob:none --sparse \
  https://github.com/okx/growth-affiliate-tool /tmp/growth-affiliate-tool
cd /tmp/growth-affiliate-tool && git sparse-checkout set skills/hermes-affiliate-mcp
cp -r skills/hermes-affiliate-mcp ~/.hermes/skills/okx-affiliate-mcp
```

Then in any Hermes session say:

> Install the OKX Affiliate MCP.

Hermes will load the skill, register a DCR client with OKX, hand you a browser auth URL,
exchange the resulting code for a token, write the bearer header into
`~/.hermes/config.yaml`, and verify the connection. End-to-end runs in ~2 minutes.

## Keeping the token alive

The OKX access_token lives 1 hour. Two ways to refresh:

- **On-demand (LLM-driven)**: just call any `mcp_okx_affiliate_*` tool. If it 401s,
  Hermes will load this skill and run `scripts/auto_refresh.py`, then retry.
- **Automatic (cron)**: schedule `scripts/auto_refresh.py` every 50 minutes — either via
  Hermes' built-in `cronjob` tool or your system crontab. See `SKILL.md` for snippets.

Hermes hot-reloads `mcp_servers` whenever `config.yaml` changes, so a token refresh
takes effect within seconds without restarting the agent.

## What's inside

```
SKILL.md                       # Hermes-readable decision tree
scripts/
  _common.py                   # shared constants + stdlib HTTP helpers
  register.py                  # one-time DCR registration
  auth.py                      # build authorize URL + PKCE
  exchange.py                  # exchange code -> token
  refresh.py                   # refresh access_token via refresh_token
  write_config.py              # inject bearer into ~/.hermes/config.yaml
  auto_refresh.py              # refresh + rewrite config (cron entry point)
  status.py                    # 1-line install state summary
reference/
  oauth-endpoints.md           # endpoint specs
  known-issues.md              # historical bugs + workarounds
  blank-callback-page.md       # what to tell the user about the broken redirect page
  openclaw-config.md           # original wiring notes (kept for reference)
  verify.md                    # smoke-test recipes
  tools-overview.md            # what each of the 6 MCP tools returns
```

## Differences from the upstream OpenClaw skill

This skill is forked from the `openclaw-affiliate-mcp` directory in
[okx/growth-affiliate-tool](https://github.com/okx/growth-affiliate-tool). Changes:

- **State directory**: `~/.hermes/data/okx-affiliate-mcp/` (was `~/.openclaw/data/...`).
- **config.yaml wiring**: new `write_config.py` injects the bearer token directly into
  `~/.hermes/config.yaml` using a delimited managed block, so Hermes' `native-mcp`
  client picks it up automatically.
- **One-shot refresh**: new `auto_refresh.py` does refresh + write_config in a single
  command — cron-friendly.
- **Status helper**: new `status.py` for the SKILL decision tree.
- **Hermes frontmatter** on `SKILL.md`.

All OAuth logic (DCR, PKCE, resource parameter, token exchange) is unchanged from upstream.

## License

[MIT](../../LICENSE) — same as the parent repository.
