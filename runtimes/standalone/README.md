# Runtime 2: standalone Python

One file, `docloop/agent.py`: a tool-calling loop, the skill library, and a
`delegate` tool that starts a subagent with a clean context.

## Run with a model

Any endpoint that speaks the OpenAI chat-completions tool format works,
including local servers and hosted routers.

```
pip install "docloop[agent]"
export OPENAI_API_KEY=...
export OPENAI_BASE_URL=...      # optional: your provider's endpoint
python -m docloop.agent examples/events/retire-csv.json --docs examples/docs --model <model-id>
```

## Run without a model

```
python -m docloop.agent examples/events/retire-csv.json --docs examples/docs --demo
```

The demo replays a fixed script for the `retire-csv` example, so you can watch
the loop, the delegation and the gate with no API key. It shows the mechanics,
not model quality.

## How the lead is built

- **System prompt:** the `docs-change-lead` skill, plus a one-line catalogue
  of the other skills.
- **Progressive disclosure:** other skills enter the context only when the
  lead calls `load_skill`.
- **Subagents:** `delegate(brief)` runs a second loop with five tools and no
  history. Its report is the only thing that returns to the lead.
- **The gate:** `approve` and `apply` are not tools. The constructor asserts it.

## What has been verified

The loop, delegation, error recovery and the scripted demo run in the test
suite. Runs against a live model were not part of the test suite.
