# Skills

Drop-in skill packs that teach AI agents how to install and operate the OKX Growth Affiliate
MCP from runtimes that do not natively handle OKX's OAuth flow.

| Skill                                                          | Description                                                  | Required for                                  |
| -------------------------------------------------------------- | ------------------------------------------------------------ | --------------------------------------------- |
| [`openclaw-affiliate-mcp`](openclaw-affiliate-mcp/SKILL.md)    | Walk an OpenClaw agent through OAuth — register / authorize / exchange / refresh — with full handling of OKX's `resource` parameter and DCR quirks | OpenClaw                                      |

> Most clients (Claude Code, Codex, Hermes, Cursor) do **not** need a skill — their MCP
> runtimes handle OAuth natively. See [`docs/install/`](../docs/install/) for direct install
> guides.

## Skill format

Each skill is a self-contained directory containing:

- `SKILL.md` — the **agent-facing** instructions. Decision tree, when-to-use triggers,
  step-by-step procedure. The agent reads this end-to-end before touching the user.
- `scripts/` — executable helpers the agent calls. Stdlib-only Python preferred (no
  `pip install` required).
- `reference/` — long-form docs the agent consults on demand: endpoint specs, known issues,
  edge cases.
- `README.md` — human-facing landing page describing why the skill exists and how to install
  it into the target runtime.

This layout is inspired by [`okx/agent-skills`](https://github.com/okx/agent-skills) — see
that repo for further skill-design conventions.

## Why some clients need a skill

The OKX OAuth server has two non-standard requirements:

1. **Mandatory `resource` parameter** ([RFC 8707](https://datatracker.ietf.org/doc/html/rfc8707))
   on every authorize and token request. Omitting it returns
   `invalid_grant: resource does not match`.
2. **Non-discovery DCR endpoint** at `/api/v5/mcp/auth/register` — clients that rely solely
   on RFC 7591 discovery will not find it.

Modern MCP clients (Claude Code, Codex, Hermes, Cursor) handle both natively. OpenClaw's
built-in MCP runtime does not yet, so the skill performs the OAuth flow with a few small
Python scripts.

## Adding a new skill

If you ship support for a new runtime that needs custom OAuth handling, mirror the
`openclaw-affiliate-mcp/` layout:

```
your-runtime-name/
├── SKILL.md                      # Decision tree — agent-facing
├── README.md                     # Human-facing
├── scripts/
│   ├── register.py
│   ├── auth.py
│   ├── exchange.py
│   └── refresh.py
└── reference/
    ├── oauth-endpoints.md
    ├── known-issues.md
    └── verify.md
```

PRs welcome.
