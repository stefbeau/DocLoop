# Runtime 1: Claude Code (or any skills-compatible agent)

No agent code at all. The agent you already use becomes the lead; this folder
gives it the skills, one subagent, the tools, and a rule that keeps it from
editing the docs directly.

## Install into a docs repository

From the root of the repository that holds your docs:

```
pip install "docloop[mcp] @ git+https://github.com/stefbeau/DocLoop"
mkdir -p .claude/skills .claude/agents
cp -r <docloop>/skills/* .claude/skills/
cp <docloop>/runtimes/claude-code/agents/*.md .claude/agents/
cp <docloop>/runtimes/claude-code/mcp.json .mcp.json
cp <docloop>/runtimes/claude-code/settings.json .claude/settings.json
```

Edit `DOCLOOP_DOCS` in `.mcp.json` if your docs are not in `docs/`, and the two
paths in `.claude/settings.json` to match.

## Use

```
> Handle the change event in events/retire-csv.json
```

The `docs-change-lead` skill takes over: classify, route, find pages, draft or
delegate to `page-drafter`, draft the notice, report, stop.

Then, as the reviewer, in a terminal:

```
docloop status retire-csv
docloop approve retire-csv --reviewer "Your Name"
docloop apply retire-csv
```

## Why the deny rule matters

A coding agent has its own file-editing tools. Without the rule in
`settings.json` it could change a page directly and skip the gate. The rule
blocks Edit and Write on the docs folder for the lead and for every subagent,
so the only way a page changes is `docloop apply`, after a recorded approval.

## What has been verified

The MCP server starts and lists its nine tools in the test suite. The skills
and the subagent file follow the documented formats. A full session inside
Claude Code was not run as part of the test suite.
