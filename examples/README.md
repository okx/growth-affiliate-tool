# Usage scenarios

Drop-in skill packs that teach an AI agent **how to use the OKX Growth Affiliate MCP**
for common analysis tasks. Each scenario describes when to trigger, which tools to call,
how to interpret the data, and what actions to recommend.

Inspired by — and structurally compatible with — the
[nuwa-skill](https://github.com/alchaincyf/nuwa-skill) `examples/` layout.

## Scenarios

| Scenario                                                                      | When the user might ask                                              |
| ----------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| [`daily-briefing`](daily-briefing/SKILL.md)                                   | "Show me yesterday's affiliate performance" / "morning report"        |
| [`high-potential-invitees`](high-potential-invitees/SKILL.md)                 | "Who should I reach out to?" / "find users worth nurturing"           |
| [`churn-rescue`](churn-rescue/SKILL.md)                                       | "Which whales are slipping away?" / "find users who stopped trading"  |
| [`whale-deep-dive`](whale-deep-dive/SKILL.md)                                 | "Pull everything on UID X" / "what's this user's history"             |
| [`acquisition-trends`](acquisition-trends/SKILL.md)                           | "Analyze my acquisition over the last N months" / "拉新趋势"            |
| [`tier-upgrade-candidates`](tier-upgrade-candidates/SKILL.md)                 | "Who should I push to VIP1?" / "Regular users doing whale volume"     |

## How an agent uses these

When the user's request matches a scenario's trigger phrases (see each `SKILL.md`'s
`description` frontmatter), the agent:

1. Loads the scenario's `SKILL.md` as its working playbook.
2. Calls the documented MCP tools in the documented order with the documented arguments.
3. Extracts the listed insights.
4. Responds with the output format the scenario specifies.
5. Offers the documented follow-ups so the user can drill deeper.

If your agent runtime supports skill packs (Claude Code, Codex, etc.), you can copy any
scenario folder into your skills directory and it will be activated automatically when the
trigger phrases appear.

## Authoring a new scenario

Mirror the existing layout:

```
your-scenario-name/
└── SKILL.md     # YAML frontmatter + when-to-use + tool sequence + sample output + follow-ups
```

Frontmatter must include:

- `name` — slug matching the folder
- `description` — trigger phrases for the agent router (keep under 900 chars for Codex
  compatibility; see [`okx/agent-skills`](https://github.com/okx/agent-skills) conventions)

Body should cover:

1. **When to use** — concrete user-intent triggers
2. **What the agent does** — step-by-step MCP tool calls with example arguments
3. **Sample output** — realistic format the user expects to receive
4. **Insights to extract** — bullet list of what the agent should look for
5. **Recommended follow-ups** — natural next actions

PRs welcome.
